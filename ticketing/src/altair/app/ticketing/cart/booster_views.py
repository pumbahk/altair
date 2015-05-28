# -*- coding:utf-8 -*-
import logging
from datetime import date
from webob.multidict import MultiDict
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.decorator import reify
from pyramid.view import view_defaults, render_view_to_response
from markupsafe import escape, Markup

from altair.formhelpers.fields import OurFormField
from altair.formhelpers.validators import DynSwitchDisabled
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.viewhelpers.numbers import create_number_formatter
from altair.app.ticketing.payments import api as payment_api
from altair.app.ticketing.payments.payment import Payment
from altair.app.ticketing.payments.exceptions import PaymentDeliveryMethodPairNotFound
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.users.models import User, UserProfile
from altair.app.ticketing.fanstatic import with_jquery, with_jquery_tools
from altair.app.ticketing.views import mobile_request
from altair.app.ticketing.models import DBSession

from . import api
from . import schemas
from .helpers import sex_value
from .events import notify_order_completed
from .exceptions import NoCartError, InvalidCSRFTokenException
from .views import PaymentView, ConfirmView, CompleteView
from .rendering import selectable_renderer
from .view_support import back, is_booster_cart_pred
from .resources import CompleteViewTicketingCartResource

from altair.app.ticketing.cart.views import jump_maintenance_page_for_trouble

logger = logging.getLogger(__name__)

# FIXME
BOOSTER_SESSION_KEY = 'booster.89ers.user_profile'

def clear_user_profile(request):
    if BOOSTER_SESSION_KEY in request.session:
        del request.session[BOOSTER_SESSION_KEY]

def store_user_profile(request, user_profile):
    logger.debug('stored user profile=%r' % user_profile)
    request.session[BOOSTER_SESSION_KEY] = user_profile

def load_user_profile(request):
    logger.debug('loaded user profile=%r' % request.session.get(BOOSTER_SESSION_KEY))
    return request.session.get(BOOSTER_SESSION_KEY)

def back_to_top2(request):
    performance_id = request.context.performance.id
    api.remove_cart(request)
    return HTTPFound(request.route_path('cart.index2', performance_id=performance_id))

def extract_field_data(field):
    if isinstance(field, OurFormField):
        return extract_form_data(field._contained_form)
    else:
        return field.data

def extract_form_data(form):
    return dict(
        (field.short_name, extract_field_data(field))
        for field in form
        if not field._validation_stopped \
           or not any(isinstance(validator, DynSwitchDisabled) for validator in field.validators)
        )

@view_defaults(
    route_name='cart.index',
    decorator=(with_jquery + with_jquery_tools).not_when(mobile_request),
    renderer=selectable_renderer('booster/index.html'),
    custom_predicates=(is_booster_cart_pred,),
    permission="buy"
    )
class BoosterEventIndexView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @lbr_view_config(request_method='GET')
    def get(self):
        jump_maintenance_page_for_trouble(self.request.organization)
        performances = set(
            sales_segment.performance
            for sales_segment in self.context.available_sales_segments
            )
        links = [
            (performance.name, self.request.route_path('cart.index2', performance_id=performance.id))
            for performance in performances
            ]
        if len(links) == 0:
            raise HTTPNotFound()
        elif len(links) == 1:
            return HTTPFound(location=links[0][1])
        else:
            return dict(links=links)

@view_defaults(
    route_name='cart.index2',
    decorator=(with_jquery + with_jquery_tools).not_when(mobile_request),
    renderer=selectable_renderer('booster/form.html'),
    custom_predicates=(is_booster_cart_pred,),
    permission="buy"
    )
class BoosterIndexView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def build_products_dict(self):
        from altair.app.ticketing.models import DBSession as session
        product_query = session.query(c_models.Product) \
            .filter(c_models.Product.sales_segment_id == self.sales_segment.id, c_models.Product.public != False) \
            .order_by(c_models.Product.display_order)
        formatter = create_number_formatter(self.request)
        return [(p.name, Markup(u'{name} ({price})'.format(name=escape(p.name), price=formatter.format_currency_html(p.price, prefer_post_symbol=True)))) for p in product_query]

    @property
    def sales_segment(self):
        return self.context.available_sales_segments[0]

    def product_form(self, params=None, data=None):
        def form_factory(formdata, name_builder, **kwargs):
            from .schemas import extra_form_type_map
            extra_form_type = extra_form_type_map[self.context.cart_setting.type]
            form = extra_form_type(formdata=formdata, name_builder=name_builder, context=self.context, **kwargs)
            form.member_type.choices = self.build_products_dict()
            return form
        fields = [
            ('extra', OurFormField(form_factory=form_factory, name_handler=u'.', field_error_formatter=None)),
            ]
        if self.context.cart_setting.flavors:
            flavors = self.context.cart_setting.flavors
        else:
            flavors = {}
        retval = schemas.ClientForm(
            flavors=flavors,
            formdata=params,
            context=self.context,
            _fields=fields
            )
        def _(f, data):
            for k, v in data.items():
                if isinstance(v, dict):
                    _(f[k], v)
                else:
                    f[k].data = v
        if params is None and data is not None:
            _(retval, data)
        return retval

    def product_form_from_user_profile(self, user_profile):
        data = {}
        default_prefecture = self.context.cart_setting.default_prefecture
        if default_prefecture is not None:
            data['prefecture'] = default_prefecture
        if user_profile is not None:
            data = user_profile
        return self.product_form(data=data)

    @lbr_view_config(request_method='GET')
    def get(self):
        jump_maintenance_page_for_trouble(self.request.organization)
        form = self.product_form_from_user_profile(load_user_profile(self.request))
        return dict(form=form)

    @lbr_view_config(request_method='POST')
    def post(self):
        jump_maintenance_page_for_trouble(self.request.organization)
        form = self.product_form(self.request.params)
        if not form.validate():
            self.request.errors = form.errors
            return dict(form=form)

        member_type = form['extra']._contained_form.member_type.data
        q = c_models.Product.query \
            .join(c_models.Product.seat_stock_type) \
            .filter(c_models.Product.sales_segment_id == self.sales_segment.id) \
            .filter(c_models.Product.name == member_type)
        product = q.one()
        cart = api.order_products(
            self.request,
            self.sales_segment,
            [(product, 1)]
            )
        if cart is None:
            logger.debug('cart is None')
            return dict(form=form)
        logger.debug('cart %s' % cart)
        api.set_cart(self.request, cart)
        data = extract_form_data(form)
        store_user_profile(self.request, data)
        logger.debug('OK redirect')
        return HTTPFound(location=self.request.route_url("cart.payment", sales_segment_id=cart.sales_segment.id))

@view_defaults(
    route_name='cart.payment',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("booster/payment.html"),
    custom_predicates=(is_booster_cart_pred,),
    permission="buy"
    )
class BoosterPaymentView(PaymentView):
    @reify
    def _user_profile(self):
        return load_user_profile(self.request)

    def get_validated_address_data(self):
        address_data = self._user_profile
        return dict(
            first_name=address_data['first_name'],
            last_name=address_data['last_name'],
            first_name_kana=address_data['first_name_kana'],
            last_name_kana=address_data['last_name_kana'],
            zip=address_data['zip'],
            prefecture=address_data['prefecture'],
            city=address_data['city'],
            address_1=address_data['address_1'],
            address_2=address_data['address_2'],
            email_1=address_data['email_1'],
            email_2=None,
            country=u"日本国",
            tel_1=address_data['tel_1'],
            tel_2=address_data['tel_2'],
            fax=address_data.get("fax"),
            sex=sex_value(address_data.get("sex"))
            )

    def get_client_name(self):
        user_profile = self._user_profile
        return user_profile['last_name'] + user_profile['first_name']

    def get_delivery_method_id(self):
        return self._user_profile['extra'].get('product_delivery_method', None)

    def get_payment_delivery_method_pairs(self, sales_segment):
        delivery_method_id = self.get_delivery_method_id()
        return [
            pdmp
            for pdmp in self.context.available_payment_delivery_method_pairs(sales_segment)
            if pdmp.payment_method.public and (delivery_method_id is None or pdmp.delivery_method.id == delivery_method_id)
            ]

    @back(back_to_top2)
    @lbr_view_config(request_method="POST")
    def post(self):
        data = load_user_profile(self.request)
        extra_data = data.get('extra')
        if extra_data is not None:
            extra_data = dict(
                (k, v)
                for k, v in extra_data.items()
                if k not in {'member_type', 'product_delivery_method'}
                )
            api.store_extra_form_data(self.request, extra_data)
        return super(BoosterPaymentView, self).post()

    @lbr_view_config(request_method="GET")
    def get(self):
        return super(BoosterPaymentView, self).get()


@view_defaults(
    route_name='payment.confirm',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("booster/confirm.html"),
    custom_predicates=(is_booster_cart_pred,),
    permission="buy")
class BoosterConfirmView(ConfirmView):
    @lbr_view_config(request_method="GET")
    def get(self):
        return super(BoosterConfirmView, self).get()

@view_defaults(
    route_name='payment.finish',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("booster/completion.html"),
    custom_predicates=(is_booster_cart_pred,))
class BoosterCompleteView(CompleteView):
    @lbr_view_config(route_name='payment.confirm', request_method="POST")
    @lbr_view_config(route_name='payment.finish.mobile', request_method="POST")
    def post(self):
        retval = super(BoosterCompleteView, self).post()
        clear_user_profile(self.request)
        return retval

    @lbr_view_config(context=CompleteViewTicketingCartResource)
    def get(self):
        return super(BoosterCompleteView, self).get()


@lbr_view_config(name="cart.contact")
def contact_view(context, request):
    return dict()
