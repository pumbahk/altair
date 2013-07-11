from zope.interface import implementer
from ticketing.login.internal.interfaces import IInternalAuthResource
from pyramid.decorator import reify
from pyramid.security import Allow, Everyone, authenticated_userid
from ticketing.operators.models import Operator, OperatorAuth
import logging
logger = logging.getLogger(__name__)

@implementer(IInternalAuthResource)
class PrintQRResource(object):
    def __init__(self, request):
        self.request = request
    __acl__ = [
        (Allow, 'group:sales_counter', 'sales_counter'), 
        (Allow, 'group:sales_counter', 'event_editor'), 
        (Allow, Everyone, 'everybody'),
    ]

    def get_after_login_url(self, *args, **kwargs):
        return self.request.route_url("eventlist", *args, **kwargs)

    @reify
    def operator(self):
        login_id = authenticated_userid(self.request)
        return Operator.query.filter(Operator.id==OperatorAuth.operator_id)\
            .filter(OperatorAuth.login_id==login_id).one()

    @reify
    def api_resource(self):
        event_id = self.request.matchdict.get("event_id", "*")
        return {
            "api.log": self.request.route_path("api.log"), 
            "api.ticket.data": self.request.route_path("api.ticket.data", event_id=event_id), 
            "api.ticketdata_from_token_id": self.request.route_path('api.applet.ticket_data'),
            "api.ticketdata_from_order_no": self.request.route_path('api.applet.ticket_data_order'),
            "api.ticket.after_printed": self.request.route_path("api.ticket.after_printed"), 
            "api.ticket.after_printed_order": self.request.route_path("api.ticket.after_printed_order"), 
            "api.ticket.refresh.printed_status": self.request.route_path("api.ticket.refresh.printed_status"), 

            "api.progress.total_result_data": self.request.route_path("api.progress.total_result_data", event_id=event_id)
            }
    @reify
    def applet_endpoints(self):
        event_id = self.request.matchdict.get("event_id", "*")
        logger.debug("tickettemplates:api -- %s" % self.request.route_path('api.applet.ticket', event_id=event_id, id=''))
        return {
            "tickettemplates": self.request.route_path('api.applet.ticket', event_id=event_id, id=''),
            "ticketdata": self.request.route_path('api.applet.ticket_data'),
            "history": self.request.route_path('api.applet.history')
            }

    @reify
    def organization(self):
        return self.operator.organization
