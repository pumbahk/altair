# -*- coding: utf-8 -*-
import logging
import webhelpers.paginate as paginate
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.path import AssetResolver
from ticketing.tickets.models import Ticket
from ticketing.views import BaseView
from . import forms

@view_defaults(decorator=with_bootstrap)
class IndexView(BaseView):
    @view_config(route_name="events.tickets.index", renderer="ticketing:templates/tickets/events/index.html")
    def index(self):
        event = self.context.event
        tickets = self.context.tickets
        return dict(event=event, tickets=tickets)

    @view_config(route_name="events.tickets.api.ticketform", renderer="ticketing:templates/tickets/events/_ticketform.html")
    def _api_ticketform(self):
        form = forms.BoundTicketForm(organization_id=self.context.user.organization_id)
        return dict(form=form)

    ## too-bad
    @view_config(route_name="events.tickets.bind.ticket", request_method="POST")
    def bind_ticket(self):
        event = self.context.event
        organization_id = self.context.user.organization_id
        form = forms.BoundTicketForm(organization_id=organization_id, 
                                     formdata=self.request.POST)
        if not form.validate():
            self.request.session.flash(u'%s' % form.errors)
            raise HTTPFound(self.request.route_path("events.tickets.index", event=event.id))

        qs = Ticket.templates_query().filter_by(organization_id=organization_id)
        ticket_template = qs.filter_by(id=form.data["ticket_template"]).one()
        bound_ticket = ticket_template.create_event_bound(event)
        bound_ticket.save()
        
        self.request.session.flash(u'チケットが登録されました')
        return HTTPFound(self.request.route_path("events.tickets.index", event_id=event.id))
