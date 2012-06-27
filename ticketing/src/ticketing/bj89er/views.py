# -*- coding:utf-8 -*-
import logging
import sqlalchemy as sa
import ticketing.core.models as c_models
import ticketing.cart.helpers as h
import ticketing.cart.api as api
from ticketing.users.models import UserProfile
from pyramid.httpexceptions import HTTPFound
from . import schemas



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
        api.set_cart(self.request, cart)
        user = self.context.get_or_create_user()
        user_profile = UserProfile(
            user=user,
        )
        logger.debug('OK redirect')
        return HTTPFound(location=self.request.route_url("cart.payment"))
