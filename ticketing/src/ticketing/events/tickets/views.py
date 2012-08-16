# -*- coding: utf-8 -*-
import logging
import webhelpers.paginate as paginate
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from ticketing.core.models import ProductItem
from ticketing.core.models import Ticket, TicketBundle, TicketBundleAttribute
from ticketing.views import BaseView
from . import forms
   

@view_defaults(decorator=with_bootstrap, permission="authenticated")
class IndexView(BaseView):
    @view_config(route_name="events.tickets.index", renderer="ticketing:templates/tickets/events/index.html")
    def index(self):
        event = self.context.event
        tickets = self.context.tickets
        bundles = self.context.bundles
        return dict(event=event, tickets=tickets, bundles=bundles)

    @view_config(route_name="events.tickets.api.ticketform", request_method="GET", 
                 renderer="ticketing:templates/tickets/events/_ticketform.html")
    def _api_ticketform(self):
        form = forms.BoundTicketForm(organization_id=self.context.user.organization_id)
        return dict(form=form)

    @view_config(route_name="events.tickets.api.bundleform", request_method="GET", 
                 renderer="ticketing:templates/tickets/events/_bundleform.html")
    def _api_ticketbundle_form(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"])
        return dict(form=form)


@view_config(route_name="events.tickets.bind.ticket", request_method="POST", 
             decorator=with_bootstrap, permission="authenticated")
def bind_ticket(request):
    event = request.context.event
    organization_id = request.context.user.organization_id
    form = forms.BoundTicketForm(organization_id=organization_id, 
                                 formdata=request.POST)
    if not form.validate():
        request.session.flash(u'%s' % form.errors)
        raise HTTPFound(request.route_path("events.tickets.index", event=event.id))

    qs = Ticket.templates_query().filter_by(organization_id=organization_id)
    ticket_template = qs.filter_by(id=form.data["ticket_template"]).one()
    bound_ticket = ticket_template.create_event_bound(event)
    bound_ticket.save()

    request.session.flash(u'チケットが登録されました')
    return HTTPFound(request.route_path("events.tickets.index", event_id=event.id))


@view_defaults(decorator=with_bootstrap, permission="authenticated")
class BundleView(BaseView):
    """ チケット券面構成(TicketBundle)
    """
    @view_config(route_name="events.tickets.bundles.new", request_method="POST")
    def bundle_new(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"], 
                                formdata=self.request.POST)
        event = self.context.event

        if not form.validate():
            self.request.session.flash(u'%s' % form.errors)
            raise HTTPFound(self.request.route_path("events.tickets.index", event=event.id))

        bundle = TicketBundle(operator=self.context.user, 
                              event_id=event.id, 
                              name=form.data["name"], 
                              )

        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.replace_product_items(ProductItem.filter(ProductItem.id.in_(form.data["product_items"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が登録されました')
        return HTTPFound(self.request.route_path("events.tickets.index", event_id=event.id))

    @view_config(route_name="events.tickets.bundles.edit", request_method="GET", 
                 renderer="ticketing:templates/tickets/events/bundles/new.html")
    def edit(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id, 
                                name=bundle.name, 
                                tickets=[e.id for e in bundle.tickets], 
                                product_items=[e.id for e in bundle.product_items])
        
        return dict(form=form, event=event, bundle=bundle)

    @view_config(route_name="events.tickets.bundles.edit", request_method="POST", 
                 renderer="ticketing:templates/tickets/events/bundles/new.html")
    def edit_post(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id, 
                                formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, event=event, bundle=bundle)

        bundle.name = form.data["name"]
        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.replace_product_items(ProductItem.filter(ProductItem.id.in_(form.data["product_items"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が更新されました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show", event_id=event.id, bundle_id=bundle.id))
        

    @view_config(route_name='events.tickets.bundles.delete', request_method="GET", 
                 renderer="ticketing:templates/tickets/events/_deleteform.html")
    def delete(self):
        bundle_id = self.request.matchdict["bundle_id"]
        event_id = self.request.matchdict["event_id"]
        message = u"このチケット券面構成(TicketBundle)を削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.bundles.delete",bundle_id=bundle_id, event_id=event_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='events.tickets.bundles.delete', request_method="POST")
    def delete_post(self):
        event_id = self.request.matchdict["event_id"]
        ## todo: check dangling object
        self.context.bundle.delete()
        self.request.session.flash(u'チケット券面構成(TicketBundle)を削除しました')
        return HTTPFound(self.request.route_path("events.tickets.index", event_id=event_id))


    @view_config(route_name="events.tickets.bundles.show",
                 renderer="ticketing:templates/tickets/events/bundles/show.html")
    def show(self):
        return dict(bundle=self.context.bundle, 
                    event=self.context.event)


@view_defaults(decorator=with_bootstrap, permission="authenticated")
class BundleAttributeView(BaseView):
    """ 属性(TicketBundleAttribute)
    """
    @view_config(route_name="events.tickets.attributes.new", request_method="GET", 
                 renderer="ticketing:templates/tickets/events/attributes/new.html")
    def new(self):
        form = forms.AttributeForm(data_value="{\n}")
        return dict(form=form,event=self.context.event)

    @view_config(route_name="events.tickets.attributes.new", request_method="POST", 
                 renderer="ticketing:templates/tickets/events/attributes/new.html")
    def new_post(self):
        bundle = self.context.bundle
        event_id = self.request.matchdict["event_id"]
        form = forms.AttributeForm(self.request.POST)
        if not form.validate():
            return dict(form=form,event=self.context.event)

        attr = TicketBundleAttribute(name=form.data["name"], 
                                     value=form.data["data_value"], 
                                     bundle=bundle)
        attr.save()
        self.request.session.flash(u'属性(TicketBundleAttribute)を追加しました')

        return self.request.route_url("events.tickets.bundles.show", event_id=event_id, bundle_id=bundle.id)
