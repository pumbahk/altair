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

from .models import TicketFormat, Ticket

import helpers

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketFormats(BaseView):
    @view_config(route_name='tickets.formats.index', renderer='ticketing:templates/tickets/formats/index.html')
    def index(self):
        return dict(h=helpers, formats=TicketFormat.query.all())

    @view_config(route_name='tickets.formats.show', renderer='ticketing:templates/tickets/formats/show.html')
    def show(self):
        return dict(h=helpers, format=TicketFormat.query.filter_by(id=self.request.matchdict['id']).one())
    

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class TicketTemplates(BaseView):
    @view_config(route_name='tickets.templates.index', renderer='ticketing:templates/tickets/templates/index.html')
    def index(self):
        pass 
