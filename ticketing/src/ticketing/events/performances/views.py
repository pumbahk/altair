 # -*- coding: utf-8 -*-

from datetime import datetime
import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import session, Event, Performance
from ticketing.events.performances.forms import PerformanceForm
from ticketing.products.models import Product
from ticketing.venues.models import Venue

@view_defaults(decorator=with_bootstrap)
class Performances(BaseView):
    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)

        class product(object):
            def __init__(self,id,name,price):
                self.id = id
                self.name = name
                self.price = price

        return {
            'performance' : performance,
            'products'      : [
                product(1, u'S席 大人', 8000),
                product(2, u'S席 子供', 8000),
                product(3, u'A席 大人', 8000),
                product(4, u'A席 子供', 8000)
            ]
        }

    @view_config(route_name='performances.new', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def new_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm()
        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='performances.new', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    def new_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(self.request.POST)
        if f.validate():
            record = Performance()
            record.event = event
            record.venue = Venue.get(f.data['venue_id'])
            record = merge_session_with_post(record, f.data)
            Performance.add(record)

            self.request.session.flash(u'パフォーマンスを登録しました')
            return HTTPFound(location=route_path('events.show', self.request))
        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='performances.edit', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def edit_get(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = PerformanceForm()
        f.process(record_to_multidict(performance))
        return {
            'form':f,
            'performance':performance,
        }

    @view_config(route_name='performances.edit', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    def edit_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = PerformanceForm(self.request.POST)
        if f.validate():
            performance.venue = Venue.get(f.data['venue_id'])
            performance = merge_session_with_post(performance, f.data)
            Performance.update(performance)

            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        else:
            return {
                'form':f,
                'performance':performance,
            }

    @view_config(route_name='performances.delete')
    def delete(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % id)

        Performance.delete(performance)

        self.request.session.flash(u'パフォーマンスを削除しました')
        return HTTPFound(location=route_path('performances.index', self.request))

