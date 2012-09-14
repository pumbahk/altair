from datetime import datetime
from dateutil import parser
from ticketing.cart.resources import TicketingCartResource
from ticketing.core.models import DBSession, Order
from ticketing.users.models import User, UserCredential, Membership, UserProfile
from ticketing.sej.models import SejOrder
from .api import load_user_profile
from sqlalchemy.orm.exc import NoResultFound
from ticketing.core.models import SalesSegment
import logging

MEMBERSHIP_NAME = '89ers'
logger = logging.getLogger(__name__)

class Bj89erCartResource(TicketingCartResource):
    def __init__(self, request):
        super(Bj89erCartResource, self).__init__(request)
        self.organization_id = request.registry.settings['89ers.organization_id']
        self.event_id = request.registry.settings['89ers.event_id']
        self.performance_id = request.registry.settings['89ers.performance_id']
        self.start_at = parser.parse(request.registry.settings['89ers.start_at'])
        self.end_at = parser.parse(request.registry.settings['89ers.end_at'])

    @property
    def sales_segment_id(self):
        #### this is tooo bad. 
        logging.debug("bj89ers sales segment is must be 1")
        return 1

    def get_sales_segment(self):
        return SalesSegment.filter_by(id=self.sales_segment_id).first()

    def get_or_create_user(self):
        from ticketing.cart import api
        cart = api.get_cart(self.request)
        credential = UserCredential.query.filter(
            UserCredential.auth_identifier==str(cart.id),
        ).filter(
            UserCredential.membership_id==Membership.id
        ).filter(
            Membership.name==MEMBERSHIP_NAME
        ).first()
        if credential:
            user = credential.user
            return user
        

        membership = Membership.query.filter(Membership.name==MEMBERSHIP_NAME).first()
        if membership is None:
            membership = Membership(name=MEMBERSHIP_NAME)
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

