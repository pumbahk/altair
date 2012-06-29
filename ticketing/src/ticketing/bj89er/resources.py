from datetime import datetime
from ticketing.cart.resources import TicketingCartResrouce
from ticketing.core.models import DBSession
from ticketing.users.models import User, UserCredential, MemberShip, UserProfile
from .api import load_user_profile

MEMBERSHIP_NAME = '89er'

class Bj89erCartResource(TicketingCartResrouce):
    def __init__(self, request):
        super(Bj89erCartResource, self).__init__(request)
        self.event_id = request.registry.settings['89er.event_id']
        self.performance_id = request.registry.settings['89er.performance_id']

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
