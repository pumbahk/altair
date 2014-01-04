# -*- coding: utf-8 -*-

import json
from StringIO import StringIO
from altair.app.ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.models import DBSession
from altair.app.ticketing.core.models import ProductItem, Performance
from altair.app.ticketing.core.models import Ticket, TicketBundle, TicketBundleAttribute, TicketPrintQueueEntry
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.tickets.response import FileLikeResponse
from . import forms

from altair.app.ticketing.tickets.utils import build_dict_from_product_item
import pystache

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class IndexView(BaseView):
    @view_config(route_name="events.tickets.index", renderer="altair.app.ticketing:templates/tickets/events/index.html")
    def index(self):
        event = self.context.event
        tickets = self.context.tickets
        bundles = self.context.bundles
        return dict(event=event, tickets=tickets, bundles=bundles)

    @view_config(route_name="events.tickets.api.ticketform", request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/_ticketform.html")
    def _api_ticketform(self):
        form = forms.BoundTicketForm(organization_id=self.context.user.organization_id)
        return dict(form=form)

    @view_config(route_name="events.tickets.api.bundleform", request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/_bundleform.html")
    def _api_ticketbundle_form(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"])
        performances = []
        return dict(form=form, performances=performances)


@view_config(route_name="events.tickets.bind.ticket", request_method="POST", 
             decorator=with_bootstrap, permission="event_editor")
def bind_ticket(request):
    event = request.context.event
    organization_id = request.context.user.organization_id
    form = forms.BoundTicketForm(organization_id=organization_id, 
                                 formdata=request.POST)
    if not form.validate():
        request.session.flash(u'%s' % form.errors)
        raise HTTPFound(request.route_path("events.tickets.index", event_id=event.id))

    qs = Ticket.templates_query().filter_by(organization_id=organization_id)
    ticket_template = qs.filter_by(id=form.data["ticket_template"]).one()
    bound_ticket = ticket_template.create_event_bound(event)
    bound_ticket.name = form.data["name"]
    bound_ticket.save()

    request.session.flash(u'チケットが登録されました')
    return HTTPFound(request.route_path("events.tickets.index", event_id=event.id))


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class BundleView(BaseView):
    """ チケット券面構成(TicketBundle)
    """
    @view_config(route_name="events.tickets.bundles.new", request_method="POST", 
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def bundle_new(self):
        form = forms.BundleForm(event_id=self.request.matchdict["event_id"], 
                                formdata=self.request.POST)
        event = self.context.event

        if not form.validate():
            return dict(form=form, event=event)

        bundle = TicketBundle(operator=self.context.user, 
                              event_id=event.id, 
                              name=form.data["name"],
                              )

        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が登録されました')
        return HTTPFound(self.request.route_path("events.tickets.index", event_id=event.id))

    @view_config(route_name="events.tickets.bundles.edit", request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def edit(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id, 
                                name=bundle.name, 
                                tickets=[e.id for e in bundle.tickets])
        performances = DBSession.query(Performance).join(ProductItem).filter(ProductItem.ticket_bundle==bundle)
        
        return dict(form=form, event=event, bundle=bundle, performances=performances)

    @view_config(route_name="events.tickets.bundles.edit", request_method="POST", 
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/new.html")
    def edit_post(self):
        bundle = self.context.bundle
        event = self.context.event
        form = forms.BundleForm(event_id=event.id, 
                                formdata=self.request.POST)
        if not form.validate():
            return dict(form=form, event=event, bundle=bundle)

        bundle.name = form.data["name"]
        bundle.replace_tickets(Ticket.filter(Ticket.id.in_(form.data["tickets"])))
        bundle.save()

        self.request.session.flash(u'チケット券面構成(TicketBundle)が更新されました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show",
                                                 event_id=event.id, bundle_id=bundle.id))
        

    @view_config(route_name='events.tickets.bundles.delete', request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/_deleteform.html")
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

        location = self.request.route_path("events.tickets.index", event_id=event_id)
        try:
            self.context.bundle.delete()
            self.request.session.flash(u'チケット券面構成(TicketBundle)を削除しました')
        except Exception, e:
            self.request.session.flash(e.message)

        return HTTPFound(location=location)

    @view_config(route_name="events.tickets.bundles.show",
                 renderer="altair.app.ticketing:templates/tickets/events/bundles/show.html")
    def show(self):
        # {<performance_id>: {<name>: "",  <products>: {}, <product_items> : {}}}
        product_item_dict = {} 
        bundle = self.context.bundle
        for product_item in bundle.product_items:
            performance = product_item_dict.get(product_item.performance_id)
            if performance is None:
                performance = product_item_dict[product_item.performance_id] = {
                    'name': u"%s(%s)" % (product_item.performance.name, product_item.performance.start_on),
                    'products': {},
                    'product_items': {}
                    }
            product = performance['products'].get(product_item.product.id)
            if product is None:
                product = performance['products'][product_item.product.id] = {
                    'name': product_item.product.name,
                    'product_items': {}
                    }
            performance['product_items'][product_item.id] = \
            product['product_items'][product_item.id] = {
                'name': product_item.name,
                'updated_at': product_item.updated_at,
                'created_at': product_item.created_at
                }
        ## for ticket-preview
        ## [{name: <performance.name>, pk: <performance.id>,  candidates: [{name: <item.name>, pk: <item.id>}, ...]}, ...]
        tickets_candidates = [{"name": t.name,  "pk": t.id, "format_id": t.ticket_format_id} for t in bundle.tickets]
        preview_item_candidates = []
        for perf_k, performance_d in product_item_dict.iteritems():
            candidates = []
            p = {"name": performance_d["name"], "pk": perf_k, "candidates": candidates}
            for item_k, item_d in performance_d["product_items"].iteritems():
                candidates.append({"name": item_d["name"], "pk": item_k, "candidates": tickets_candidates})
            preview_item_candidates.append(p)
        return dict(bundle=self.context.bundle, 
                    event=self.context.event,
                    product_item_dict=product_item_dict, 
                    preview_item_candidates=json.dumps(preview_item_candidates))


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class BundleAttributeView(BaseView):
    """ 属性(TicketBundleAttribute)
    """
    @view_config(route_name="events.tickets.attributes.new", request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def new(self):
        form = forms.AttributeForm(data_value="{\n}")
        return dict(form=form,event=self.context.event)

    @view_config(route_name="events.tickets.attributes.new", request_method="POST", 
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def new_post(self):
        bundle = self.context.bundle
        event_id = self.request.matchdict["event_id"]
        form = forms.AttributeForm(self.request.POST, bundle_id=bundle.id)
        if not form.validate():
            return dict(form=form,event=self.context.event)

        attr = TicketBundleAttribute(name=form.data["name"], 
                                     value=form.data["value"], 
                                     ticket_bundle=bundle)
        attr.save()
        self.request.session.flash(u'属性(TicketBundleAttribute)を追加しました')

        return HTTPFound(self.request.route_url("events.tickets.bundles.show", event_id=event_id, bundle_id=bundle.id))

    @view_config(route_name="events.tickets.attributes.edit", request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def edit(self):
        bundle_attribute = self.context.bundle_attribute
        form = forms.AttributeForm(name=bundle_attribute.name, 
                                       value=bundle_attribute.value, 
                                       bundle_id=bundle_attribute.ticket_bundle_id, 
                                       attribute_id=bundle_attribute.id)
        return dict(form=form, event=self.context.event, attribute=bundle_attribute)

    @view_config(route_name="events.tickets.attributes.edit", request_method="POST", 
                 renderer="altair.app.ticketing:templates/tickets/events/attributes/new.html")
    def edit_post(self):
        attribute = self.context.bundle_attribute
        form = forms.AttributeForm(self.request.POST, 
                                       bundle_id=attribute.ticket_bundle_id, 
                                       attribute_id=attribute.id)


        if not form.validate():
            return dict(form=form,event=self.context.event, attribute=attribute)

        attribute.name = form.data["name"]
        attribute.value = form.data["value"]
        attribute.save()

        self.request.session.flash(u'属性(TicketBundleAttribute)を更新しました')
        kwargs = dict(event_id=self.request.matchdict["event_id"], 
                      bundle_id=attribute.ticket_bundle_id)
        return HTTPFound(self.request.route_url("events.tickets.bundles.show", **kwargs))

    @view_config(route_name='events.tickets.attributes.delete', request_method="GET", 
                 renderer="altair.app.ticketing:templates/tickets/events/_deleteform.html")
    def delete(self):
        attribute_id = self.request.matchdict["attribute_id"]
        bundle_id = self.request.matchdict["bundle_id"]
        event_id = self.request.matchdict["event_id"]
        message = u"この属性(TicketBundleAttribute)を削除します。よろしいですか？"
        next_to = self.request.route_path("events.tickets.attributes.delete",
                                          attribute_id=attribute_id, 
                                          bundle_id=bundle_id,
                                          event_id=event_id)
        return dict(message=message, next_to=next_to)

    @view_config(route_name='events.tickets.attributes.delete', request_method="POST")
    def delete_post(self):
        event_id = self.request.matchdict["event_id"]
        bundle_id = self.request.matchdict["bundle_id"]
        self.context.bundle_attribute.delete()
        self.request.session.flash(u'"属性(TicketBundleAttribute)を削除しました')
        return HTTPFound(self.request.route_path("events.tickets.bundles.show",
                                                 event_id=event_id, bundle_id=bundle_id))
