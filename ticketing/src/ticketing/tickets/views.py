# -*- coding: utf-8 -*-
import logging

import webhelpers.paginate as paginate
from ticketing.fanstatic import with_bootstrap
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path
from pyramid.response import Response
from pyramid.path import AssetResolver

from ticketing.views import BaseView

from ticketing.core.models import DeliveryMethod
from .models import TicketFormat, Ticket
from . import forms
import helpers

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
    @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html', request_method="GET")
    def index(self):
        return dict(h=helpers, formats=TicketFormat.query.all())

    @view_config(route_name='tickets.formats.new', renderer='ticketing:templates/tickets/formats/new.html')
    def new(self):
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id)
        return dict(h=helpers, form=form)

    @view_config(route_name='tickets.formats.new', renderer='ticketing:templates/tickets/formats/new.html', request_method="POST")
    def new_post(self):
        form = forms.TicketFormatForm(organization_id=self.context.user.organization_id, 
                                      formdata=self.request.POST)
        if not form.validate():
            return dict(h=helpers, form=form)
        
        params = form.data
        ticket_format = TicketFormat(name=params["name"], 
                                data=params["data_value"], 
                                )
        for dmethod in DeliveryMethod.filter(DeliveryMethod.id.in_(form.data["delivery_methods"])):
            ticket_format.delivery_methods.append(dmethod)
        ticket_format.save()
        return HTTPFound(location=self.request.route_path("tickets.formats.index"))
            

    @view_config(route_name='tickets.formats.show', renderer='ticketing:templates/tickets/formats/show.html')
    def show(self):
        return dict(h=helpers, format=TicketFormat.query.filter_by(id=self.request.matchdict['id']).one())
    

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketTemplates(BaseView):
    @view_config(route_name='tickets.templates.index', renderer='ticketing:templates/tickets/templates/index.html')
    def index(self):
        pass 
