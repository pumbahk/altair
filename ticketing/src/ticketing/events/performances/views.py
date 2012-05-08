# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, Performance, Account
from ticketing.events.performances.forms import PerformanceForm, StockHolderForm
from ticketing.products.models import Product, StockHolder, SalesSegment

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        products = Product.find(performance_id=performance_id)
        user = self.context.user
        accounts = Account.get_by_organization_id(user.organization_id)
        sales_segments = SalesSegment.get_by_organization_id(user.organization_id)

        return {
            'performance':performance,
            'products':products,
            'accounts':accounts,
            'sales_segments':sales_segments,
        }

    @view_config(route_name='performances.new', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def new_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = PerformanceForm(organization_id=self.context.user.organization_id)
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

        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            performance = merge_session_with_post(Performance(), f.data)
            performance.event_id = event_id
            performance.venue_id = f.data['venue_id']
            performance.save()

            self.request.session.flash(u'パフォーマンスを登録しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
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

        f = PerformanceForm(organization_id=self.context.user.organization_id)
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

        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            performance = merge_session_with_post(performance, f.data)
            performance.venue_id = f.data['venue_id']
            performance.save()

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

        performance.delete()

        self.request.session.flash(u'パフォーマンスを削除しました')
        return HTTPFound(location=route_path('events.show', self.request, event_id=performance.event_id))

    @view_config(route_name='performances.stock_holder.new', request_method='POST')
    def new_stock_holder(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = StockHolderForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            stock_holder = merge_session_with_post(StockHolder(), f.data)
            stock_holder.performance_id = performance.id
            stock_holder.save()
            self.request.session.flash(u'枠を保存しました')

        return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
