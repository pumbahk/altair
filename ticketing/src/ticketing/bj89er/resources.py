from ticketing.cart.resources import TicketingCartResrouce
from ticketing.core.models import DBSession
from ticketing.users.models import User, UserCredential, MemberShip

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
            MemberShip.name=='89er'
        ).first()
        if credential:
            return credential.user
        
        user = User()
        membership = MemberShip.query.filter(MemberShip.name=='89er').first()
        if membership is None:
            membership = MemberShip(name='89er')
            DBSession.add(membership)
        credential = UserCredential(user=user, auth_identifier=str(cart.id), membership=membership)
        DBSession.add(user)
        return user
