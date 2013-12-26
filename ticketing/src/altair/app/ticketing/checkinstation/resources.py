from zope.interface import implementer
from altair.app.ticketing.login.internal.interfaces import IInternalAuthResource
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, authenticated_userid
from altair.app.ticketing.operators.models import Operator, OperatorAuth
import logging
logger = logging.getLogger(__name__)

@implementer(IInternalAuthResource)
class CheckinStationResource(object):
    def __init__(self, request):
        self.request = request
    __acl__ = [
        (Allow, 'group:sales_counter', 'sales_counter'), 
        (Allow, 'group:sales_counter', 'event_editor'), 
        (Allow, Everyone, 'everybody'),
    ]

    def get_after_login_url(self, *args, **kwargs):
        return self.request.route_url("eventlist", *args, **kwargs)

    def login_validate(self, form):
        return form.validate()

    @reify
    def operator(self):
        login_id = authenticated_userid(self.request)
        return Operator.query.filter(Operator.id==OperatorAuth.operator_id)\
            .filter(OperatorAuth.login_id==login_id).one()

    @reify
    def organization(self):
        return self.operator.organization
