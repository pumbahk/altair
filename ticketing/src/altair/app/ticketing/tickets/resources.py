# coding=utf-8
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.core.models import Ticket, Event, TicketBundle, TicketFormat, Ticket_TicketBundle, Performance
from altair.app.ticketing.resources import TicketingAdminResource
from sqlalchemy import and_


class TicketsResource(TicketingAdminResource):
    __name__ = 'tickets'

    def after_ticket_action_redirect(self, template=None):
        if template is None or not template.derived_tickets:
            return HTTPFound(location=self.request.route_path("tickets.index"))
        else:
            return HTTPFound(location=self.request.route_path("tickets.templates.update_derivatives", id=template.id)) 

    def tickets_query(self):
        return Ticket.templates_query()

    @reify
    def performance_id(self):
        try:
            return int(self.request.params.get('performance_id'))
        except (TypeError, ValueError):
            return None

    @reify
    def performance(self):
        if not self.performance_id:
            return None
        return Performance.query.join(Event)\
            .filter(Performance.id == self.performance_id, Event.organization == self.organization).first()

    @reify
    def ticket_formats(self):
        # パフォーマンスIDがある場合は全商品の券面構成に紐づくチケット様式、無い場合はORGに紐づくチケット様式を返却します。
        if self.performance:
            bundle_ids = [item.ticket_bundle_id for item in self.performance.product_items]
            if not bundle_ids:
                return []
            ticket_formats = TicketFormat.query \
                .join(Ticket, and_(Ticket.ticket_format_id == TicketFormat.id,
                                   Ticket.organization_id == TicketFormat.organization_id)) \
                .join(Ticket_TicketBundle, Ticket_TicketBundle.ticket_id == Ticket.id) \
                .join(TicketBundle, and_(TicketBundle.id == Ticket_TicketBundle.ticket_bundle_id,
                                         TicketBundle.event_id == Ticket.event_id)) \
                .filter(TicketFormat.organization == self.performance.event.organization,
                        TicketBundle.event == self.performance.event,
                        TicketBundle.id.in_(bundle_ids))
        else:
            ticket_formats = TicketFormat.query.filter_by(organization=self.organization)
        return ticket_formats.order_by(TicketFormat.display_order).distinct()
