from datetime import datetime
from dateutil import parser
from ticketing.cart.resources import TicketingCartResource
from ticketing.core.models import DBSession
from ticketing.users.models import User, UserCredential, MemberShip, UserProfile
from ticketing.orders.models import Order
from ticketing.sej.models import SejOrder
from .api import load_user_profile
from sqlalchemy.orm.exc import NoResultFound

MEMBERSHIP_NAME = '89ers'

class Bj89erCartResource(TicketingCartResource):
    def __init__(self, request):
        super(Bj89erCartResource, self).__init__(request)
        self.organization_id = request.registry.settings['89ers.organization_id']
        self.event_id = request.registry.settings['89ers.event_id']
        self.performance_id = request.registry.settings['89ers.performance_id']
        self.start_at = parser.parse(request.registry.settings['89ers.start_at'])
        self.end_at = parser.parse(request.registry.settings['89ers.end_at'])

    def get_or_create_user(self):
        from ticketing.cart import api
        cart = api.get_cart(self.request)
        credential = UserCredential.query.filter(
            UserCredential.auth_identifier==str(cart.id),
        ).filter(
            UserCredential.membership_id==MemberShip.id
        ).filter(
            MemberShip.name==MEMBERSHIP_NAME
        ).first()
        if credential:
            user = credential.user
            return user
        

        membership = MemberShip.query.filter(MemberShip.name==MEMBERSHIP_NAME).first()
        if membership is None:
            membership = MemberShip(name=MEMBERSHIP_NAME)
            DBSession.add(membership)

        user = User()
        credential = UserCredential(user=user, auth_identifier=str(cart.id), membership=membership)
        credential = user.user_credential
        DBSession.add(user)
        return user

    def get_order(self):
        order_no = self.request.params.get('order_no')
        order = Order.filter_by(
            organization_id = self.organization_id,
            order_no = order_no
        ).first()
        sej_order = None

        payment_method_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin.id
        if payment_method_plugin_id == 1:
            pass
        elif payment_method_plugin_id == 3:
            sej_order = SejOrder.filter(SejOrder.order_id == "%012d" % int(order_no)).first()

        return order, sej_order


