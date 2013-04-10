from pyramid.security import Allow, Everyone, Authenticated, authenticated_userid

from ticketing.operators.models import (
    OperatorAuth, 
    OperatorRole, 
    Operator
)

from ticketing.core.models import Event
from ticketing.lots.models import Lot

class LotResource(object):
    def __init__(self, request):
        self.request = request




    acl = [
        (Allow, Everyone , 'everybody'),
        (Allow, Authenticated , 'authenticated'),
        (Allow, 'login' , 'everybody'),
        (Allow, 'api' , 'api'),
    ]

    @property
    def __acl__(self):

        roles = OperatorRole.all()
        acl = []
        for role in roles:
            for permission in role.permissions:
                acl.append((Allow, role.name, permission.category_name))
        return self.acl + acl

    @property
    def user(self):
        user_id = authenticated_userid(self.request)
        # assign the operator object to the context
        user = Operator.get_by_login_id(user_id) if user_id is not None else None
        return user

    @property
    def lot(self):
        lot_id = self.request.matchdict.get('lot_id')
        if not lot_id:
            return None

        return Lot.query.filter(Lot.id==lot_id).first()

    @property
    def event(self):
        event_id = self.request.matchdict.get('event_id')
        if not event_id:
            return None

        return Event.query.filter(Event.id==event_id).first()
