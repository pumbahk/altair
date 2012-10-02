from pyramid.decorator import reify
from pyramid.security import Allow

class PrintQRResource(object):
    def __init__(self, request):
        self.request = request
    __acl__ = [
        (Allow, 'group:sales_counter', 'sales_counter')
    ]

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
        from ticketing.core.models import Organization
        return Organization.query.filter_by(id=1).first()

    @reify
    def user(self):
        return self.organization.user
