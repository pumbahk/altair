# -*- coding: utf-8 -*-

import logging

import webhelpers.paginate as paginate
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict, DBSession
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, Performance, Account, SalesSegment
from ticketing.events.performances.forms import PerformanceForm
from ticketing.events.stock_holders.forms import StockHolderForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.products.models import Product
from ticketing.products.forms import ProductForm, ProductItemForm
from ticketing.events.stock_types.forms import StockTypeForm, StockAllocationForm

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.index', renderer='ticketing:templates/performances/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)

        sort = self.request.GET.get('sort', 'Performance.id')
        direction = self.request.GET.get('direction', 'asc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Performance.filter(Performance.event_id==event_id)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=20,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'event':event,
            'performances':performances,
            'form':PerformanceForm(organization_id=self.context.user.organization_id),
        }

    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    @view_config(route_name='performances.show_tab', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        data = {'performance':performance}

        tab = self.request.matchdict.get('tab', 'venue-designer')
        if tab == 'seat-allocation':
            data['form_stock_holder'] = StockHolderForm(organization_id=self.context.user.organization_id, performance_id=performance_id)
        elif tab == 'product':
            data['form_product'] = ProductForm(event_id=performance.event_id)
            data['form_product_item'] = ProductItemForm(user_id=self.context.user.id, performance_id=performance_id)
        elif tab == 'reservation':
            pass
        elif tab == 'ticket-designer':
            pass
        else:
            data['form_stock_type'] = StockTypeForm(event_id=performance.event_id)
            data['form_stock_allocation'] = StockAllocationForm()

        return data

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
            performance.create_venue_id = f.data['venue_id']
            performance.save()

            self.request.session.flash(u'パフォーマンスを保存しました')
            return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='performances.edit', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='GET', renderer='ticketing:templates/performances/edit.html')
    def edit_get(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = PerformanceForm(organization_id=self.context.user.organization_id)
        f.process(record_to_multidict(performance))
        f.venue_id.data = performance.venue.original_venue_id

        if self.request.matched_route.name == 'performances.copy':
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':performance.event,
        }

    @view_config(route_name='performances.edit', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    @view_config(route_name='performances.copy', request_method='POST', renderer='ticketing:templates/performances/edit.html')
    def edit_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = PerformanceForm(self.request.POST, organization_id=self.context.user.organization_id)
        if f.validate():
            connection = DBSession.bind.connect()
            try:
                tran = connection.begin()

                if self.request.matched_route.name == 'performances.copy':
                    event_id = performance.event_id
                    performance = merge_session_with_post(Performance(), f.data)
                    performance.event_id = event_id
                    performance.create_venue_id = f.data['venue_id']
                else:
                    performance = merge_session_with_post(performance, f.data)
                    if f.data['venue_id'] != performance.venue.original_venue_id:
                        performance.delete_venue_id = performance.venue.id
                        performance.create_venue_id = f.data['venue_id']
                performance.save()

                tran.commit()
                logging.debug('performance save success')

                self.request.session.flash(u'パフォーマンスを保存しました')
                return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id))
            except Exception, e:
                tran.rollback()
                logging.error('performance save failed %s' % e.message)
            finally:
                tran.close()

        return {
            'form':f,
            'event':performance.event,
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
