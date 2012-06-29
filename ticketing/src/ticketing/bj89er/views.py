# -*- coding:utf-8 -*-
import logging
import sqlalchemy as sa
import ticketing.core.models as c_models
from ..orders import models as o_models
import ticketing.cart.helpers as h
import ticketing.cart.api as api
from ticketing.users.models import UserProfile
from pyramid.httpexceptions import HTTPFound
from . import schemas
from .api import load_user_profile
from ticketing.cart.views import PaymentView as _PaymentView


logger = logging.getLogger(__name__)

class IndexView(object):
    def __init__(self, request):
        self.request = request
        self.context = request.context


    def __call__(self):
        return dict()

    def get(self):
        event = c_models.Event.query.filter_by(id=self.context.event_id).one()

        salessegment = self.context.get_sales_segument()

        query = c_models.Product.query
        #query = query.filter(c_models.Product.id.in_(q))
        query = query.order_by(sa.desc("price"))
        query = h.products_filter_by_salessegment(query, salessegment)


        products = [dict(name=p.name, price=h.format_number(p.price, ","), id=p.id)
                    for p in query]
        return dict(products=products)

    @property
    def ordered_items(self):
        number = int(self.request.params['number'])
        product_id = self.request.params['member_type']
        product = c_models.Product.query.filter_by(id=product_id).one()
        return [(product, number)]

    def post(self):
        cart = self.context.order_products(self.context.performance_id, self.ordered_items)
        if cart is None:
            logger.debug('cart is None')
            return dict()
        logger.debug('cart %s' % cart)
        api.set_cart(self.request, cart)
        user = self.context.get_or_create_user()
        user_profile = UserProfile(
            user=user,
        )
        self.request.session['bj89er.user_profile'] = dict(self.request.params)
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
            #country=params['country'],
            country=u"日本国",
            tel_1=params['tel1_1'] + params['tel1_2'] + params['tel1_3'],
            tel_2=params['tel2_1'] + params['tel2_2'] + params['tel2_3'],
            #fax=params['fax'],
            user=user,
        )
        return shipping_address

    def get_client_name(self):
        user_profile = load_user_profile(self.request)
        return user_profile['last_name'] + user_profile['first_name']

    def get_mail_address(self):
        user_profile = load_user_profile(self.request)
        return user_profile['email']
