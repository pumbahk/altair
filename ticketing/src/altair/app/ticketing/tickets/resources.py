from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.core.models import Ticket
from altair.app.ticketing.resources import TicketingAdminResource

class TicketsResource(TicketingAdminResource):
    __name__ = 'tickets'

    def after_ticket_action_redirect(self, template=None):
        if template is None or not template.derived_tickets:
            return HTTPFound(location=self.request.route_path("tickets.index"))
        else:
            return HTTPFound(location=self.request.route_path("tickets.templates.update_derivatives", id=template.id)) 

    def tickets_query(self):
        return Ticket.templates_query()
