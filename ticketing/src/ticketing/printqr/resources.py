from pyramid.decorator import reify
from pyramid.security import Allow, authenticated_userid
from ticketing.operators.models import Operator, OperatorAuth

class PrintQRResource(object):
    def __init__(self, request):
        self.request = request
    __acl__ = [
        (Allow, 'group:sales_counter', 'sales_counter')
    ]

    @reify
    def operator(self):
        login_id = authenticated_userid(self.request)
        return Operator.query.filter(Operator.id==OperatorAuth.operator_id)\
            .filter(OperatorAuth.login_id==login_id).one()

    @reify
    def api_resource(self):
        return {
            "api.ticket.data": self.request.route_url("api.ticket.data")
            }

    @reify
    def applet_endpoints(self):
        return {
            "formats": self.request.route_path("api.applet.formats"), 
            "peek": self.request.route_path("api.applet.peek"), 
            "dequeue": self.request.route_path("api.applet.dequeue"), 
            }

    @reify
    def organization(self):
        return self.operator.organization

    @reify
    def user(self):
        return self.organization.user
