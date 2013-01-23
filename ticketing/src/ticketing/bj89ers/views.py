# -*- coding:utf-8 -*-
import logging
from datetime import datetime, date
import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config, render_view_to_response
from pyramid.view import notfound_view_config
from webob.multidict import MultiDict
import transaction

from ..cart.events import notify_order_completed
from ..cart.exceptions import NoCartError
from ..cart.views import PaymentView as _PaymentView, CompleteView as _CompleteView
from ..cart import api as cart_api
from ..payments import payment as payment_api # XXX: aodag!
from ..cart import helpers as h
from ..core import models as c_models

from ..users.models import SexEnum
from ..users.models import User, UserProfile

from . import schemas
from .api import load_user_profile, store_user_profile, remove_user_profile
from .models import DBSession
from .helpers import sex_value

logger = logging.getLogger(__name__)

@view_config(context=NoCartError)
def no_cart(context, request):
    logger.error("No cart!")
    return HTTPFound(request.route_url('index'))

def cart_creation_exception(context, request):
    if context.back_url is not None:
        # カートの救済可能な場合
        cart_api.recover_cart(request) 
        transaction.commit()
        return HTTPFound(location=context.back_url)
    else:
        # カートの救済不可能
        if cart is not None:
            location = request.route_url('cart.index', event_id=cart.performance.event_id)
        else:
            location = request.context.host_base_url
    return dict(message=Markup(u'決済中にエラーが発生しました。しばらく時間を置いてから<a href="%s">再度お試しください。</a>' % location))


def back(func):
    def retval(*args, **kwargs):
        request = get_current_request()
        if request.params.get('back'):
            return HTTPFound(request.route_url('index'))
        return func(*args, **kwargs)
    return retval

class IndexView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    def _create_form(self, params):
        salessegment = self.context.get_sales_segument()
        query = c_models.Product.query
        query = query.filter(c_models.Product.event_id == self.context.event_id)
        query = query.order_by(sa.desc("price"))
        query = h.products_filter_by_salessegment(query, salessegment)
        products = dict()
        for p in query:
            products[str(p.id)] = p

        form = schemas.OrderFormSchema(params)
        choices = [(str(p.id), u"%s (%s円)" % (p.name, h.format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form, products

    def notready(self):
        return dict(start_at=self.context.start_at, end_at=self.context.end_at)

    def get(self):
        current_date = datetime.now()
        if current_date < self.context.start_at or self.context.end_at < current_date:
            return HTTPFound(location=self.request.route_url('notready'))
        user_profile = load_user_profile(self.request)
        form, products = self._create_form(MultiDict(user_profile) if user_profile else MultiDict())
        return dict(form=form, products=products)

    @property
    def ordered_items(self):
        number = 1
        product_id = self.request.params['member_type']
        product = c_models.Product.query.filter_by(id=product_id).one()
        return [(product, number)]

    def post(self):
        form,products = self._create_form(self.request.params)
        if not form.validate():
            self.request.errors = form.errors
            logger.debug("%s" % form.errors)
            return dict(form=form, products=products)

        cart = self.context.order_products(self.context.performance_id, self.ordered_items)
        if cart is None:
            logger.debug('cart is None')
            return dict(form=form, products=products)
        logger.debug('cart %s' % cart)
        cart_api.set_cart(self.request, cart)
        store_user_profile(self.request, form.data)
        logger.debug('OK redirect')
        sales_segment_id = self.context.sales_segment_id
        cart.sales_segment_id = sales_segment_id
        return HTTPFound(location=self.request.route_url("cart.payment", sales_segment_id=sales_segment_id))

class PaymentView(_PaymentView):
    def get_validated_address_data(self):
        address_data = load_user_profile(self.request)
        return dict(
            first_name=address_data['first_name'],
            last_name=address_data['last_name'],
            first_name_kana=address_data['first_name_kana'],
            last_name_kana=address_data['last_name_kana'],
            zip=address_data['zipcode1'] + address_data['zipcode2'],
            prefecture=address_data['prefecture'],
            city=address_data['city'],
            address_1=address_data['address1'],
            address_2=address_data['address2'],
            email_1=address_data['email_1'],
            email_2=None,
            country=u"日本国",
            tel_1=address_data['tel_1'],
            tel_2=address_data['tel_2'],
            fax=None
            )

    def get_client_name(self):
        user_profile = load_user_profile(self.request)
        return user_profile['last_name'] + user_profile['first_name']

    def get_mail_address(self):
        user_profile = load_user_profile(self.request)
        return user_profile['email_1']

    @back
    def post(self):
        return super(self.__class__, self).post()

class CompleteView(_CompleteView):
    @back
    def __call__(self):
        cart = cart_api.get_cart_safe(self.request)

        order_session = self.request.session['order']

        payment_delivery_method_pair_id = order_session['payment_delivery_method_pair_id']
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id
        ).one()

        payment_delivery_plugin = payment_api.get_payment_delivery_plugin(self.request,
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            order = payment_delivery_plugin.finish(self.request, cart)
        else:
            payment_plugin = payment_api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            order = payment_plugin.finish(self.request, cart)
            DBSession.add(order)
            delivery_plugin = payment_api.get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
            delivery_plugin.finish(self.request, cart)

        profile = load_user_profile(self.request)

        # これ本当にいるの??
        order.user = User(
            user_profile=UserProfile(
                email_1=profile['email_1'],
                first_name=profile['first_name'], 
                last_name=profile['last_name'],
                first_name_kana=profile['first_name_kana'],
                last_name_kana=profile['last_name_kana'],
                birth_day=date(int(profile['year']), int(profile['month']), int(profile['day'])),
                sex=sex_value(profile['sex']),
                zip=profile['zipcode1'] + u'-' + profile['zipcode2'],
                country='Japan',
                prefecture=profile['prefecture'],
                city=profile['city'],
                address_1=profile['address1'],
                address_2=profile['address2'],
                tel_1=profile['tel_1'],
                tel_2=profile['tel_2'],
                fax='',
                status=0
                )
            )

        order.organization_id = order.performance.event.organization_id

        # productは一個しか来ない
        order_product = order.items[0]
        for ordered_product_item in order_product.ordered_product_items:
            product_item = ordered_product_item.product_item
            # Tシャツ
            if product_item.stock.stock_type.name == u'Tシャツ':
                ordered_product_item.attributes['t_shirts_size'] = profile.get('t_shirts_size')
            else:
                # これ本当にいるの??
                for k, v in profile.items():
                    if k != 't_shirts_size':
                        ordered_product_item.attributes[k] = v

        notify_order_completed(self.request, order)

        remove_user_profile(self.request)

        return dict(order=order)


class OrderReviewView(object):

    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        response = render_view_to_response(form, self.request, name="order_review_form")
        if response is None:
            raise ValueError
        return response

    @property
    def order_not_found_message(self):
        return [u'受付番号または電話番号が違います。']

    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            response = render_view_to_response(form, self.request, name="order_review_form")
            if response is None:
                raise ValueError
            return response

        order, sej_order = self.context.get_order()
        if not order or \
           order.shipping_address is None or ( \
           order.shipping_address.tel_1 != form.data.get('tel') and \
           order.shipping_address.tel_2 != form.data.get('tel')):

            self.request.errors = form.errors
            self.request.errors['order_no'] = self.order_not_found_message

            response = render_view_to_response(form, self.request, name="order_review_form")
            if response is None:
                raise ValueError
            return response

        else:
            return dict(order=order, sej_order=sej_order)

@view_config(name="order_review_form")
def order_review_form_view(form, request):
    return dict(form=form)

def exception_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

def notfound_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()
def forbidden_view(context, request):
    logger.error("The error was: %s" % context, exc_info=request.exc_info)
    return dict()

@view_config(name="contact")
def contact_view(context, request):
    return dict()
