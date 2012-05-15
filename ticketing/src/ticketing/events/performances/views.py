# -*- coding: utf-8 -*-

import webhelpers.paginate as paginate

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.url import route_path

from ticketing.models import merge_session_with_post, record_to_multidict, DBSession
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.events.models import Event, Performance, Account, SalesSegment
from ticketing.events.performances.forms import PerformanceForm, StockHolderForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.products.models import Product, StockHolder

@view_defaults(decorator=with_bootstrap, permission="event_editor")
class Performances(BaseView):

    @view_config(route_name='performances.index', renderer='ticketing:templates/performances/index.html')
    def index(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id)

        current_page = int(self.request.params.get('page', 0))
        sort = self.request.GET.get('sort', 'Performance.id')
        direction = self.request.GET.get('direction', 'desc')
        if direction not in ['asc', 'desc']: direction = 'asc'

        page_url = paginate.PageURL_WebOb(self.request)
        query = DBSession.query(Performance).filter(Performance.event_id == event_id)
        query = query.order_by(sort + ' ' + direction)

        performances = paginate.Page(query, page=current_page, items_per_page=5, url=page_url)

        return {
            'event':event,
            'performances':performances,
        }

    @view_config(route_name='performances.show', renderer='ticketing:templates/performances/show.html')
    def show(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        products = Product.find(performance_id=performance_id)
        user = self.context.user
        accounts = Account.get_by_organization_id(user.organization_id)

        form_ss = SalesSegmentForm()
        return {
            'performance':performance,
            'products':products,
            'accounts':accounts,
            'user':user,
            'form_ss':form_ss,
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


@view_defaults(decorator=with_bootstrap, permission="event_editor")
class StockHolders(BaseView):

    @view_config(route_name='performances.stock_holder.new', request_method='POST')
    def new_post(self):
        performance_id = int(self.request.matchdict.get('performance_id', 0))
        performance = Performance.get(performance_id)
        if performance is None:
            return HTTPNotFound('performance id %d is not found' % performance_id)

        f = StockHolderForm(self.request.POST, organization_id=self.context.user.organization_id)
        #if f.validate():
        data = f.data
        style = {
            'stroke' : {
                'color'     : data.get('stroke_color'),
                'width'     : data.get('stroke_width'),
                'pattern'   : data.get('stroke_patten'),
                },
            'fill': {
                'color'     : data.get('fill_color'),
                'type'      : data.get('fill_type'),
                'image'     : data.get('fill_image'),
                },
            'text'          : data.get('text'),
            'text_color'    : data.get('text_color'),
        }
        stock_holder = merge_session_with_post(StockHolder(), data)
        stock_holder.style = style

        stock_holder.performance_id = performance.id
        stock_holder.save()
        self.request.session.flash(u'枠を保存しました')
        #else:
        #    self.request.session.flash(u'枠を保存できません')

        return HTTPFound(location=route_path('performances.show', self.request, performance_id=performance.id, _anchor='seat-allocation'))
