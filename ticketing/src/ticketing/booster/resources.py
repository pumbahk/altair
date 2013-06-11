from datetime import datetime
from dateutil import parser
import sqlalchemy as sa
from ticketing.cart.resources import TicketingCartResource
from ticketing.core.models import DBSession, Order, Product
from ticketing.users.models import User, UserCredential, Membership, UserProfile
from ticketing.sej.models import SejOrder
from .api import load_user_profile
from sqlalchemy.orm.exc import NoResultFound
from ticketing.core.models import SalesSegment
from pyramid.decorator import reify
import logging

from .api import get_booster_settings
from ticketing.cart.helpers import products_filter_by_salessegment
logger = logging.getLogger(__name__)

class BoosterCartResource(TicketingCartResource):
    @reify
    def membership_name(self):
        return get_booster_settings(self.request).membership_name

    def _populate_params(self):
        self._event_id = get_booster_settings(self.request).event_id
        self._sales_segment_id = None

    @reify 
    def product_query(self):
        query = Product.query
        query = query.filter(Product.event_id == self.event_id)
        query = query.order_by(sa.desc("price"))

        salessegment = self.get_sales_segment()
        return products_filter_by_salessegment(query, salessegment)

    @reify
    def sales_segment(self):
        return self.available_sales_segments[0]

    def get_or_create_user(self):
        from ticketing.cart import api
        cart = api.get_cart(self.request)
        credential = UserCredential.query.filter(
            UserCredential.auth_identifier==str(cart.id),
        ).filter(
            UserCredential.membership_id==Membership.id
        ).filter(
            Membership.name==self.membership_name
        ).first()
        if credential:
            user = credential.user
            return user
        

        membership = Membership.query.filter(Membership.name==self.membership_name).first()
        if membership is None:
            membership = Membership(name=self.membership_name)
            DBSession.add(membership)

        user = User()
        credential = UserCredential(user=user, auth_identifier=str(cart.id), membership=membership)
        credential = user.user_credential
        DBSession.add(user)
        return user

    def get_order(self):
        order_no = self.request.params.get('order_no')
        order = Order.filter_by(
            organization_id=self.organization_id,
            order_no=order_no
        ).first()
        logger.debug("organization_id=%s, order_no=%s, order=%s" % (self.organization_id, order_no, order))
        sej_order = None
        if order:
            payment_method_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin.id
            if payment_method_plugin_id == 1:
                pass
            elif payment_method_plugin_id == 3:
                sej_order = SejOrder.filter(SejOrder.order_id == order_no).first()

        return order, sej_order

