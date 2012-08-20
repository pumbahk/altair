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

    def after_ticket_action_redirect(self):
        return HTTPFound(location=self.request.route_path("tickets.templates.index"))
    
    def tickets_query(self):
        return Ticket.templates_query()
