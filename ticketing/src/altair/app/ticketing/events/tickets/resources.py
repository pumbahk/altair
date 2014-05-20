from pyramid.interfaces import IRootFactory
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.decorator import reify
from altair.app.ticketing.core.models import Event
from altair.app.ticketing.core.models import Ticket, TicketBundle, TicketBundleAttribute, ProductItem, TicketFormat,TicketFormat_DeliveryMethod
from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID

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

    @reify
    def event(self):
        event = Event.filter_by(organization_id=self.organization.id, id=self.request.matchdict["event_id"]).first()
        if event is None:
            raise HTTPNotFound('event id %s is not found' % self.request.matchdict["event_id"])
        return event

    @reify
    def bundle(self):
        mdict = self.request.matchdict
        bundle = TicketBundle.filter_by(id=mdict["bundle_id"], event_id=mdict["event_id"]).first()
        if bundle is None:
            raise HTTPNotFound('bundle id %s is not found' % mdict["bundle_id"])
        return bundle

    @reify
    def bundle_attribute(self):
        mdict = self.request.matchdict
        attribute = TicketBundleAttribute.filter_by(ticket_bundle_id=mdict["bundle_id"], 
                                        id=mdict["attribute_id"]).first()
        if attribute is None:
            raise HTTPNotFound('attribute id %s is not found' % mdict["attribute_id"])
        return attribute

    @reify
    def ticket_template(self):
        mdict = self.request.matchdict
        template = Ticket.filter_by(id=mdict["template_id"]).first()
        if template is None:
            raise HTTPNotFound('template id %s is not found' % mdict["template_id"])
        return template

    @reify
    def product_item(self):
        mdict = self.request.matchdict
        item = ProductItem.filter_by(id=mdict["item_id"]).first()
        if item is None:
            raise HTTPNotFound('item id %s is not found' % mdict["item_id"])
        return item

    @reify
    def ticket_templates(self):
        return Ticket.filter_by(organization_id=self.organization.id, event_id=None)

    @reify
    def tickets(self):
        return Ticket.filter_by(organization_id=self.organization.id, event_id=self.request.matchdict["event_id"])

    @reify
    def ticket_something_else_formats(self):
        return TicketFormat.filter_by(organization_id=self.organization.id)

    @reify
    def ticket_sej_formats(self):
        return (TicketFormat.filter_by(organization_id=self.organization.id)
                .filter(TicketFormat.id==TicketFormat_DeliveryMethod.ticket_format_id,
                        TicketFormat_DeliveryMethod.delivery_method_id==DeliveryMethod.id, 
                        DeliveryMethod.delivery_plugin_id==SEJ_DELIVERY_PLUGIN_ID))

    @reify
    def bundles(self):
        return TicketBundle.filter_by(event_id=self.request.matchdict["event_id"])
