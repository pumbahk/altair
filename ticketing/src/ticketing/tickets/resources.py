from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPFound
from ticketing.core.models import Ticket

class TicketsResource(object):
    __name__ = 'tickets'

    ## too-bad
    def __init__(self, request):
        self.request = request
        parent = self.request.registry.getUtility(IRootFactory)(self.request)

        if not hasattr(self, "__acl__") and parent and hasattr(parent, "__acl__"):
            self.__acl__ = parent.__acl__
        self.user = parent.user

    def after_ticket_action_redirect(self, template=None):
        if template is None or not template.derived_tickets:
            return HTTPFound(location=self.request.route_path("tickets.index"))
        else:
            return HTTPFound(location=self.request.route_path("tickets.templates.update_derivatives", id=template.id)) 

    def tickets_query(self):
        return Ticket.templates_query()
