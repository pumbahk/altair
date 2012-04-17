 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.models import *

import webhelpers.paginate as paginate
from .forms import TicketerForm
from ..models import Ticketer

import sqlahelper
session = sqlahelper.get_session()

@view_defaults(decorator=with_bootstrap)
class Ticketers(BaseView):

    @view_config(route_name='ticketers.index' , renderer='ticketing:templates/ticketers/index.html')
    def index(self):
        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)
        query = session.query(Ticketer)
        ticketers = paginate.Page(query.order_by(Ticketer.id), current_page, url=page_url)
        return {
            'ticketers'        : ticketers
        }


    @view_config(route_name='ticketers.show' , renderer='ticketing:templates/ticketers/show.html')
    def show(self):

        ticketer_id = int(self.request.matchdict.get("ticketer_id", 0))
        ticketer = Ticketer.get(ticketer_id)
        if ticketer is None:
            return HTTPNotFound("ticketer id %d is not found" % ticketer_id)

        current_page = int(self.request.params.get("page", 0))
        page_url = paginate.PageURL_WebOb(self.request)

        return {
            'ticketer' : ticketer,
        }

    @view_config(route_name='ticketers.new' , request_method="GET" , renderer='ticketing:templates/ticketers/new.html')
    def new_get(self):
        return {}

    @view_config(route_name='ticketers.new' , request_method="POST" , renderer='ticketing:templates/ticketers/new.html')
    def new_post(self):
        f = TicketerForm()
        if f.validate():
            data = f.data
            record = Ticketer()
            record = merge_session_with_post(record, data)
            Ticketer.add(record)
            return self.location('ticketers.index')
        else:
            return {
                'form':f
            }

    @view_config(route_name='ticketers.edit' , request_method="GET" , renderer='ticketing:templates/ticketers/edit.html')
    def edit_get(self):
        ticketer_id = int(self.request.matchdict.get("ticketer_id", 0))
        ticketer = Ticketer.get(ticketer_id)
        if ticketer is None:
            return HTTPNotFound("client id %d is not found" % ticketer_id)

        app_structs = record_to_multidict(ticketer)
        f = TicketerForm()
        f.process(app_structs)
        print app_structs
        return {
            'form' :f,
            'ticketer' : ticketer
        }

    @view_config(route_name='ticketers.edit' , request_method="POST" , renderer='ticketing:templates/ticketers/edit.html')
    def edit_post(self):
        ticketer_id = int(self.request.matchdict.get("ticketer_id", 0))
        ticketer = Ticketer.get(ticketer_id)
        if ticketer is None:
            return HTTPNotFound("client id %d is not found" % ticketer_id)
        f = TicketerForm(self.request.POST)
        if f.validate():
            data = f.data
            record = merge_session_with_post(ticketer, data)
            Event.update(record)
            return HTTPFound(location=route_path('ticketers.show', self.request, ticketer_id=ticketer_id))
        else:
            return {
                'form':f
            }

