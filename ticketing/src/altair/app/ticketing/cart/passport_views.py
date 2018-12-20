# -*- coding:utf-8 -*-
import logging
from datetime import datetime, timedelta
from altair.sqlahelper import get_db_session

from altair.app.ticketing.cart.views import jump_maintenance_page_for_trouble
from altair.app.ticketing.core import models as c_models
from altair.app.ticketing.fanstatic import with_jquery, with_jquery_tools
from altair.app.ticketing.views import mobile_request
from altair.formhelpers.fields import OurFormField
from altair.formhelpers.validators import DynSwitchDisabled
from altair.pyramid_dynamic_renderer import lbr_view_config
from altair.request.adapters import UnicodeMultiDictAdapter
from altair.viewhelpers.numbers import create_number_formatter
from markupsafe import escape, Markup
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_defaults

from . import api
from . import schemas
from .helpers import sex_value
from .rendering import selectable_renderer
from .resources import CompleteViewTicketingCartResource
from .view_support import back, is_passport_cart_pred
from .views import PaymentView, ConfirmView, CompleteView
from ..passport.api import validate_passport_data, validate_passport_order, get_passport_product_quantities, \
    get_passport_user_from_order_id
from ..passport.models import PassportUser

logger = logging.getLogger(__name__)

PASSPORT_SESSION_KEY = 'altair.cart.passport.user_profile'


def clear_user_profile(request, performance_id):
    session_key = "{}{}".format(PASSPORT_SESSION_KEY, performance_id)
    if session_key in request.session:
        del request.session[session_key]


def store_user_profile(request, user_profile, performance_id):
    logger.debug('stored user profile=%r' % user_profile)
    request.session["{}{}".format(PASSPORT_SESSION_KEY, performance_id)] = user_profile


def load_user_profile(request, performance_id):
    logger.debug('loaded user profile=%r' % request.session.get(PASSPORT_SESSION_KEY))
    return request.session.get("{}{}".format(PASSPORT_SESSION_KEY, performance_id))


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
    renderer=selectable_renderer('passport/index.html'),
    custom_predicates=(is_passport_cart_pred,),
    permission="buy"
)
class PassportEventIndexView(object):
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
    renderer=selectable_renderer('passport/form.html'),
    custom_predicates=(is_passport_cart_pred,),
    permission="buy"
)
class PassportIndexView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = get_db_session(request, name="slave")

    def build_products_dict(self):

        product_query = self.session.query(c_models.Product) \
            .filter(c_models.Product.sales_segment_id == self.sales_segment.id, c_models.Product.public is not False) \
            .order_by(c_models.Product.display_order)
        formatter = create_number_formatter(self.request)
        return [(p.name, Markup(u'{name} ({price})'.format(name=escape(p.name),
                                                           price=formatter.format_currency_html(p.price,
                                                                                                prefer_post_symbol=True))))
                for p in product_query]

    @property
    def sales_segment(self):
        return self.context.available_sales_segments[0]

    def product_form(self, params=None, data=None):
        from altair.app.ticketing.cart.view_support import get_extra_form_class
        extra_form_type = get_extra_form_class(self.request, self.context.cart_setting)

        def form_factory(formdata, name_builder, **kwargs):
            form = extra_form_type(formdata=formdata, name_builder=name_builder, context=self.context, **kwargs)
            return form

        fields = [
            ('extra', OurFormField(form_factory=form_factory, name_handler=u'.', field_error_formatter=None)),
        ]
        retval = schemas.ClientForm(
            formdata=params,
            context=self.context,
            flavors=(self.context.cart_setting.flavors or {}),
            _fields=fields
        )

        def _(f, data):
            for k, v in data.items():
                if isinstance(v, dict):
                    _(f[k], v)
                else:
                    try:
                        f[k].data = v
                    except KeyError:
                        logger.info("deleted extra_form data. performance_id={}, key_name={}".format(
                            self.context.performance.id, k.encode('utf-8')))

        if params is None and data is not None:
            _(retval, data)
        if issubclass(extra_form_type, schemas.PassportExtraForm):
            extra_form_fields = retval['extra']._contained_form._form_schema
        else:
            extra_form_fields = None
        return retval, extra_form_fields

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
        form, extra_form_fields = self.product_form_from_user_profile(
            load_user_profile(self.request, self.context.performance.id))
        return dict(form=form, extra_form_fields=extra_form_fields, max_quantity=self.sales_segment.max_quantity)

    @lbr_view_config(request_method='POST')
    def post(self):
        jump_maintenance_page_for_trouble(self.request.organization)
        form, extra_form_fields = self.product_form(UnicodeMultiDictAdapter(self.request.params, 'utf-8', 'replace'))
        if not form.validate():
            self.request.errors = form.errors
            return dict(form=form, extra_form_fields=extra_form_fields, max_quantity=self.sales_segment.max_quantity)

        data = extract_form_data(form)
        if not validate_passport_data(extra_data=data):
            self.request.session.flash(u'パスポート購入で1人分のデータが正常に入っていない箇所があります')
            return dict(form=form, extra_form_fields=extra_form_fields, max_quantity=self.sales_segment.max_quantity)

        if not validate_passport_order(extra_data=data):
            self.request.session.flash(u'同じ種類のパスポートを購入する場合は続けてご入力ください')
            return dict(form=form, extra_form_fields=extra_form_fields, max_quantity=self.sales_segment.max_quantity)

        q = c_models.Product.query \
            .join(c_models.Product.seat_stock_type) \
            .filter(c_models.Product.sales_segment_id == self.sales_segment.id) \
            .filter(c_models.Product.public == True)
        products = q.all()

        if not self.context.performance.passport:
            # パスポート機能が有効じゃない場合ここから進めない
            return HTTPNotFound()

        passport_quantities = get_passport_product_quantities(products, data)

        cart = api.order_products(
            self.request,
            self.sales_segment,
            passport_quantities
        )
        if cart is None:
            logger.debug('cart is None')
            return dict(form=form, extra_form_fields=extra_form_fields, max_quantity=self.sales_segment.max_quantity)
        logger.debug('cart %s' % cart)
        api.set_cart(self.request, cart)
        store_user_profile(self.request, data, cart.performance_id)
        logger.debug('OK redirect')
        return HTTPFound(location=self.request.route_url("cart.payment", sales_segment_id=cart.sales_segment.id))


@view_defaults(
    route_name='cart.payment',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("passport/payment.html"),
    custom_predicates=(is_passport_cart_pred,),
    permission="buy"
)
class PassportPaymentView(PaymentView):
    @reify
    def _user_profile(self):
        return load_user_profile(self.request, self.context.performance.id)

    def get_validated_address_data(self, pdp=None):
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
            email_2=address_data.get('email_2'),  # optional
            country=u"日本",
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
            if
            pdmp.payment_method.public and (delivery_method_id is None or pdmp.delivery_method.id == delivery_method_id)
        ]

    @back(back_to_top2)
    @lbr_view_config(request_method="POST")
    def post(self):
        data = load_user_profile(self.request, self.context.performance.id)
        extra_data = data.get('extra')
        if extra_data is not None:
            extra_data = dict(
                (k, v)
                for k, v in extra_data.items()
                if k not in {'member_type', 'product_delivery_method'}
            )
            api.store_extra_form_data(self.request, extra_data)
        return super(PassportPaymentView, self).post()

    @lbr_view_config(request_method="GET")
    def get(self):
        return super(PassportPaymentView, self).get()


@view_defaults(
    route_name='payment.confirm',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("passport/confirm.html"),
    custom_predicates=(is_passport_cart_pred,),
    permission="buy")
class PassportConfirmView(ConfirmView):
    @lbr_view_config(request_method="GET")
    def get(self):
        return super(PassportConfirmView, self).get()


@view_defaults(
    route_name='payment.finish',
    decorator=with_jquery.not_when(mobile_request),
    renderer=selectable_renderer("passport/completion.html"),
    custom_predicates=(is_passport_cart_pred,))
class PassportCompleteView(CompleteView):
    @lbr_view_config(route_name='payment.confirm', request_method="POST")
    @lbr_view_config(route_name='payment.finish.mobile', request_method="POST")
    def post(self):
        performance_id = self.context.performance.id
        retval = super(PassportCompleteView, self).post()
        clear_user_profile(self.request, performance_id)
        return retval

    @lbr_view_config(context=CompleteViewTicketingCartResource)
    def get(self):
        # Orderに紐づくPassportUserがいる場合は作成しない
        if not get_passport_user_from_order_id(self.context.order_like.id):
            passport_dict = self.create_passport_dict(self.context.order_like.attributes)
            for item in self.context.order_like.items:
                for _ in range(item.quantity):
                    passport_user = PassportUser()
                    passport_user.is_valid = True
                    passport_user.ordered_product_id = item.id
                    passport_user.order_id = self.context.order_like.id
                    passport_user.passport_id = self.context.performance.passport[0].id
                    passport_user.expired_at = datetime.now() + timedelta(
                        days=self.context.performance.passport[0].available_day)
                    passport_user.order_attribute_num = passport_dict[str(item.product.display_order)].pop(0)
                    passport_user.save()
        return super(PassportCompleteView, self).get()

    def create_passport_dict(self, order_attributes):
        # 追加情報で入力された種類のvalueをキーにしている
        # そしてそのvalueが、Productのdisplay_orderと一致している。
        # 複数同じパスポートが買われている場合、リストに追加される
        passport_dict = {}
        for num in range(4):
            index = num + 1
            try:
                passport = order_attributes[u"種類({0}人目)".format(index)]
                if passport in passport_dict:
                    passport_dict[passport].append(index)
                else:
                    passport_dict[passport] = [index]
            except KeyError:
                pass
        return passport_dict
