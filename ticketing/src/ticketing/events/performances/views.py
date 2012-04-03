 # -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ..models import session, Event, Performance
from .forms import PerformanceForm
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap

from datetime import datetime

import webhelpers.paginate as paginate

@view_defaults(decorator=with_bootstrap)
class Performances(BaseView):
    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get("performance_id", 0))
        performance = Performance.get(performance_id)

        class product(object):
            def __init__(self,id,name,price):
                self.id = id
                self.name = name
                self.price = price

        return {
            'performance'   : performance,
            'products'      : [
                product(1, u'S席 大人', 8000),
                product(2, u'S席 子供', 8000),
                product(3, u'A席 大人', 8000),
                product(4, u'A席 子供', 8000)
            ]
        }
    @view_config(route_name='performances.new', request_method="GET", renderer='ticketing:templates/performances/new.html')
    def new_get(self):
        event_id = int(self.request.matchdict.get("event_id", 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound("event id %d is not found" % event_id)

        f = PerformanceForm()
        return {
            'event' : event,
            'form' : f
        }

    @view_config(route_name='performances.new', request_method="POST", renderer='ticketing:templates/performances/new.html')
    def new_post(self):
        event_id = int(self.request.matchdict.get("event_id", 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound("event id %d is not found" % event_id)

        f = PerformanceForm(self.request.POST)
        if f.validate():
            data = f.data
            record = Performance()
            record = merge_session_with_post(record, data)
            Performance.add(record)
            return HTTPFound(location=route_path('events.index', self.request))
        return {
            'event' : event,
            'form' : f
        }

    @view_config(route_name='performances.new', renderer='ticketing:templates/performances/new.html')
    def edit(self):
        return {
            'form' : PerformanceForm()
        }