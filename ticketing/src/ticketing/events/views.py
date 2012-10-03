# -*- coding: utf-8 -*-
import os
import isodate
import json
import logging
import urllib2
import contextlib
from datetime import datetime

import webhelpers.paginate as paginate
from sqlalchemy import or_
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path
from pyramid.response import Response
from pyramid.path import AssetResolver

from ticketing.models import merge_session_with_post, record_to_multidict
from ticketing.views import BaseView
from ticketing.fanstatic import with_bootstrap
from ticketing.core.models import Event, Performance, StockType, StockTypeEnum
from ticketing.events.forms import EventForm
from ticketing.events.performances.forms import PerformanceForm
from ticketing.events.sales_segments.forms import SalesSegmentForm
from ticketing.events.stock_types.forms import StockTypeForm
from ticketing.events.stock_holders.forms import StockHolderForm
from ticketing.products.forms import ProductForm

from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi


@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Events(BaseView):

    @view_config(route_name='events.index', renderer='ticketing:templates/events/index.html', permission='event_viewer')
    def index(self):
        sort = self.request.GET.get('sort', 'Event.id')
        direction = self.request.GET.get('direction', 'desc')
        if direction not in ['asc', 'desc']:
            direction = 'asc'

        query = Event.filter(Event.organization_id==int(self.context.user.organization_id))
        query = query.order_by(sort + ' ' + direction)

        # search condition
        if self.request.method == 'POST':
            condition = self.request.POST.get('event')
            if condition:
                condition = '%' + condition + '%'
                query = query.filter(or_(Event.code.like(condition), Event.title.like(condition)))
            condition = self.request.POST.get('performance')
            if condition:
                condition = '%' + condition + '%'
                query = query.join(Event.performances)\
                            .filter(or_(Performance.code.like(condition), Performance.name.like(condition)))

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=10,
            url=paginate.PageURL_WebOb(self.request)
        )

        return {
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'events':events,
        }

    @view_config(route_name='events.show', renderer='ticketing:templates/events/show.html', permission='event_viewer')
    def show(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        accounts = event.get_accounts()

        return {
            'event':event,
            'accounts':accounts,
            'seat_stock_types':StockType.filter_by(event_id=event_id, type=StockTypeEnum.Seat.v).all(),
            'non_seat_stock_types':StockType.filter_by(event_id=event_id, type=StockTypeEnum.Other.v).all(),
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'form_stock_type':StockTypeForm(event_id=event_id),
            'form_stock_holder':StockHolderForm(organization_id=self.context.user.organization_id, event_id=event_id),
            'form_sales_segment':SalesSegmentForm(event_id=event_id),
            'form_product':ProductForm(event_id=event.id),
        }

    @view_config(route_name='events.new', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def new_get(self):
        f = EventForm(organization_id=self.context.user.organization.id)
        event = Event(organization_id=self.context.user.organization_id)

        event_id = int(self.request.matchdict.get('event_id', 0))
        if event_id:
            event = Event.get(event_id, organization_id=self.context.user.organization_id)
            if event is None:
                return HTTPNotFound('event id %d is not found' % event_id)

        event = record_to_multidict(event)
        if 'id' in event: event.pop('id')
        f.process(event)

        return {
            'form':f,
        }

    @view_config(route_name='events.new', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def new_post(self):
        f = EventForm(self.request.POST, organization_id=self.context.user.organization.id)

        if f.validate():
            event = merge_session_with_post(Event(organization_id=self.context.user.organization_id), f.data)
            event.save()

            self.request.session.flash(u'イベントを登録しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
            }

    @view_config(route_name='events.edit', request_method='GET', renderer='ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='GET', renderer='ticketing:templates/events/edit.html')
    def edit_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(organization_id=self.context.user.organization.id)
        f.process(record_to_multidict(event))

        if self.request.matched_route.name == 'events.copy':
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='events.edit', request_method='POST', renderer='ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='POST', renderer='ticketing:templates/events/edit.html')
    def edit_post(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(self.request.POST, organization_id=self.context.user.organization.id)
        if f.validate():
            if self.request.matched_route.name == 'events.copy':
                event = merge_session_with_post(Event(organization_id=self.context.user.organization_id), f.data)
            else:
                event = merge_session_with_post(event, f.data)
            event.save()

            self.request.session.flash(u'イベントを保存しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
                'event':event,
            }

    @view_config(route_name='events.delete')
    def delete(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        event.delete()

        self.request.session.flash(u'イベントを削除しました')
        return HTTPFound(location=route_path('events.index', self.request))

    @view_config(route_name='events.send')
    def send(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        try:
            data = {
                'events':[event.get_cms_data()],
                'created_at':isodate.datetime_isoformat(datetime.now()),
                'updated_at':isodate.datetime_isoformat(datetime.now()),
            }
        except Exception, e:
            logging.info("cms build data error: %s (event_id=%s)" % (e.message, event_id))
            self.request.session.flash(e.message)
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))

        communication_api = get_communication_api(self.request, CMSCommunicationApi)
        req = communication_api.create_connection('api/event/register', json.dumps(data))

        try:
            with contextlib.closing(urllib2.urlopen(req)) as res:
                if res.getcode() == HTTPCreated.code:
                    self.request.session.flash(u'イベントをCMSへ送信しました')
                else:
                    raise urllib2.HTTPError(code=res.getcode())
        except urllib2.HTTPError, e:
            logging.warn("cms sync http error: response status url=(%s) %s" % (e.code, e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.code)
        except urllib2.URLError, e:
            logging.warn("cms sync http error: response status url=(%s) %s" % (e.reason, e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.reason)
        except Exception, e:
            logging.error("cms sync error: %s, %s" % (e.reason, e.message))
            self.request.session.flash(u'イベント送信に失敗しました')

        return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
