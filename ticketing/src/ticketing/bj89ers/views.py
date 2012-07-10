# -*- coding:utf-8 -*-
import logging
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.orm.exc import NoResultFound
import ticketing.core.models as c_models
from ..orders import models as o_models
import ticketing.cart.helpers as h
import ticketing.cart.api as api
import ticketing.bj89ers.api as bj89ers_api
from ticketing.users.models import UserProfile
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from . import schemas
from .models import DBSession
from .api import load_user_profile
from ticketing.cart.views import PaymentView as _PaymentView, CompleteView as _CompleteView
from ticketing.users.models import SexEnum
from ticketing.cart.events import notify_order_completed

logger = logging.getLogger(__name__)

class IndexView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context


    def __call__(self):
        return dict()

    def _create_form(self):
        salessegment = self.context.get_sales_segument()
        query = c_models.Product.query
        query = query.filter(c_models.Product.event_id == self.context.event_id)
        query = query.order_by(sa.desc("price"))
        query = h.products_filter_by_salessegment(query, salessegment)

        products = dict()
        for p in query:
            products[str(p.id)] = p

        form = schemas.OrderFormSchema(self.request.params)
        choices = [(str(p.id), u"%s (%s円)" % (p.name, h.format_number(p.price, ","))) for p in query]
        form.member_type.choices = choices
        return form, products

    def get(self):
        current_date = datetime.now()
        if current_date < self.context.start_at or self.context.end_at < current_date:
            return render_to_response('carts/ready.html',dict(), self.request)

        form,products = self._create_form()
        return dict(form=form,products=products)

    @property
    def ordered_items(self):
        number = 1
        product_id = self.request.params['member_type']
        product = c_models.Product.query.filter_by(id=product_id).one()
        return [(product, number)]

    def post(self):
        form,products = self._create_form()
        if not form.validate():
            self.request.errors = form.errors
            return self.get()

        cart = self.context.order_products(self.context.performance_id, self.ordered_items)
        if cart is None:
            logger.debug('cart is None')
            return dict(form=form, products=products)
        logger.debug('cart %s' % cart)
        api.set_cart(self.request, cart)
        bj89ers_api.store_user_profile(self.request, dict(self.request.params))
        logger.debug('OK redirect')
        return HTTPFound(location=self.request.route_url("cart.payment"))

class PaymentView(_PaymentView):
    def validate(self):
        return None

    def create_shipping_address(self, user):
        params = load_user_profile(self.request)
        logger.debug('user_profile %s' % params)
        shipping_address = o_models.ShippingAddress(
            first_name=params['first_name'],
            last_name=params['last_name'],
            first_name_kana=params['first_name_kana'],
            last_name_kana=params['last_name_kana'],
            zip=params['zipcode1'] + params['zipcode2'],
            prefecture=params['prefecture'],
            city=params['city'],
            address_1=params['address1'],
            address_2=params['address2'],
            email=params['email'],
            #country=params['country'],
            #country=u"日本国",
            tel_1=params['tel1_1'] + params['tel1_2'] + params['tel1_3'],
            tel_2=params['tel2_1'] + params['tel2_2'] + params['tel2_3'],
            #fax=params['fax'],
            user=None,
        )
        return shipping_address

    def get_client_name(self):
        user_profile = load_user_profile(self.request)
        return user_profile['last_name'] + user_profile['first_name']

    def get_mail_address(self):
        user_profile = load_user_profile(self.request)
        return user_profile['email']

class CompleteView(_CompleteView):

    def __call__(self):
        assert api.has_cart(self.request)
        cart = api.get_cart(self.request)

        order_session = self.request.session['order']

        payment_delivery_method_pair_id = order_session['payment_delivery_method_pair_id']
        payment_delivery_pair = c_models.PaymentDeliveryMethodPair.query.filter(
            c_models.PaymentDeliveryMethodPair.id==payment_delivery_method_pair_id
        ).one()

        payment_delivery_plugin = api.get_payment_delivery_plugin(self.request,
            payment_delivery_pair.payment_method.payment_plugin_id,
            payment_delivery_pair.delivery_method.delivery_plugin_id,)
        if payment_delivery_plugin is not None:
            order = payment_delivery_plugin.finish(self.request, cart)
        else:
            payment_plugin = api.get_payment_plugin(self.request, payment_delivery_pair.payment_method.payment_plugin_id)
            order = payment_plugin.finish(self.request, cart)
            DBSession.add(order)
            delivery_plugin = api.get_delivery_plugin(self.request, payment_delivery_pair.delivery_method.delivery_plugin_id)
            delivery_plugin.finish(self.request, cart)

        order.organization_id = order.performance.event.organization_id

        profile = bj89ers_api.load_user_profile(self.request)

        # productは一個しか来ない
        order_product = order.items[0]
        for ordered_product_item in order_product.ordered_product_items:
            product_item = ordered_product_item.product_item
            # Tシャツ
            if product_item.stock.stock_type.type == c_models.StockTypeEnum.Other.v:
                ordered_product_item.put('t_shirts_size', profile['t_shirts_size'])
            else:
                for k, v in profile.items():
                    if k != 't_shirts_size':
                        ordered_product_item.put(k, v)

        notify_order_completed(self.request, order)


        return dict(order=order)

class OrderReviewView(object):

    def __init__(self, request):
        self.request = request
        self.context = request.context

    def __call__(self):
        return dict()

    def get(self):
        form = schemas.OrderReviewSchema(self.request.params)
        return render_to_response('order_review/form.html',dict(form=form), self.request)

    @property
    def order_not_found_message(self):
        return [u'オーダーIDまたは電話番号が違います。']

    def post(self):
        form = schemas.OrderReviewSchema(self.request.params)
        if not form.validate():
            self.request.errors = form.errors
            return self.get()
        try:
            order = o_models.Order.filter_by(
                organization_id = self.context.organization_id,
                order_no = form.data.get('order_no')
            ).one()

        except NoResultFound, e:
            self.request.errors = form.errors
            self.request.errors['order_no'] = self.order_not_found_message
            return self.get()

        if order.shipping_address is None or order.shipping_address.tel_1== form.tel or \
                                                order.shipping_address.tel_2 == form.tel:
            self.request.errors = form.errors
            self.request.errors['order_no'] = self.order_not_found_message
            return self.get()
        else:
            return dict(order=order)
