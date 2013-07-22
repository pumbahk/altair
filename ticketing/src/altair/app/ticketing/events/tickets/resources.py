from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from altair.app.ticketing.core.models import Event
from altair.app.ticketing.core.models import Ticket, TicketBundle, TicketBundleAttribute, ProductItem
from altair.app.ticketing.resources import TicketingAdminResource

class EventBoundTicketsResource(TicketingAdminResource):
    __name__ = 'events.tickets'

    def after_ticket_action_redirect(self, template=None):
        if template is None or not template.derived_tickets:
            return HTTPFound(location=self.request.route_path("events.tickets.index", event_id=self.request.matchdict["event_id"]))
        else:
            return HTTPFound(location=self.request.route_path("tickets.templates.update_derivatives", id=template.id)) 
    
    def tickets_query(self):
        return Ticket.filter_by(event_id=self.request.matchdict["event_id"])

    @property
    def event(self):
        event = Event.filter_by(organization_id=self.user.organization_id, id=self.request.matchdict["event_id"]).first()
        if event is None:
            raise HTTPNotFound('event id %s is not found' % self.request.matchdict["event_id"])
        return event

    @property
    def bundle(self):
        mdict = self.request.matchdict
        bundle = TicketBundle.filter_by(id=mdict["bundle_id"], event_id=mdict["event_id"]).first()
        if bundle is None:
            raise HTTPNotFound('bundle id %s is not found' % mdict["bundle_id"])
        return bundle

    @property
    def bundle_attribute(self):
        mdict = self.request.matchdict
        attribute = TicketBundleAttribute.filter_by(ticket_bundle_id=mdict["bundle_id"], 
                                        id=mdict["attribute_id"]).first()
        if attribute is None:
            raise HTTPNotFound('attribute id %s is not found' % mdict["attribute_id"])
        return attribute

    @property
    def ticket_template(self):
        mdict = self.request.matchdict
        template = Ticket.filter_by(id=mdict["template_id"]).first()
        if template is None:
            raise HTTPNotFound('template id %s is not found' % mdict["template_id"])
        return template

    @property
    def product_item(self):
        mdict = self.request.matchdict
        item = ProductItem.filter_by(id=mdict["item_id"]).first()
        if item is None:
            raise HTTPNotFound('item id %s is not found' % mdict["item_id"])
        return item

    @property
    def tickets(self):
        return Ticket.filter_by(organization_id=self.user.organization_id, event_id=self.request.matchdict["event_id"])

    @property
    def bundles(self):
        return TicketBundle.filter_by(event_id=self.request.matchdict["event_id"])
