# -*- coding: utf-8 -*-

import os
import isodate
import json
import re
import urllib2
import contextlib
from datetime import datetime, timedelta
from dateutil.parser import parse as parsedate
import logging

import webhelpers.paginate as paginate
from sqlalchemy import or_
from sqlalchemy import sql
from sqlalchemy.orm.util import class_mapper
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPCreated
from pyramid.threadlocal import get_current_registry
from pyramid.url import route_path
from pyramid.response import Response
from pyramid.path import AssetResolver
from paste.util.multidict import MultiDict

from altair.sqlahelper import get_db_session
from altair.sqla import new_comparator

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict, merge_and_flush
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, EventSetting, Performance, StockType, StockTypeEnum, SalesSegment
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.events.performances.forms import PerformanceForm
from altair.app.ticketing.events.stock_types.forms import StockTypeForm
from altair.app.ticketing.events.stock_holders.forms import StockHolderForm

from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi
from .api import get_cms_data
from .forms import EventForm, EventSearchForm
from .helpers import EventHelper
from altair.app.ticketing.carturl.api import get_cart_url_builder, get_cart_now_url_builder
logger = logging.getLogger()

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Events(BaseView):

    @view_config(route_name='events.index', renderer='altair.app.ticketing:templates/events/index.html', permission='event_viewer')
    def index(self):
        slave_session = get_db_session(self.request, name="slave")

        sort_column = self.request.params.get('sort', 'display_order')
        try:
            mapper = class_mapper(Event)
            prop = mapper.get_property(sort_column)
            sort = new_comparator(prop,  mapper)
        except:
            sort = None
        direction = { 'asc': sql.asc, 'desc': sql.desc }.get(
            self.request.GET.get('direction'),
            sql.asc
            )

        query = slave_session.query(Event) \
            .group_by(Event.id) \
            .filter(Event.organization_id==int(self.context.organization.id))
        if sort is not None:
            query = query.order_by(direction(sort))
        query = query.order_by(sql.desc(Event.id))

        form_search = EventSearchForm(self.request.params)
        search_query = None
        if form_search.validate():
            query = self.context.need_join(query, form_search)
            query = self.context.create_like_where(query, form_search.event_name_or_code.data, Event.code, Event.title)
            query = self.context.create_like_where(query, form_search.performance_name_or_code.data, Performance.code, Performance.name)
            query = self.context.create_range_where(query, form_search.perf_range_start.data, form_search.perf_range_end.data, Performance.start_on, Performance.end_on)
            query = self.context.create_range_where(query, form_search.deal_range_start.data, form_search.deal_range_end.data, SalesSegment.start_at, SalesSegment.end_at)
            query = self.context.create_where(query, form_search.perf_open_start.data, form_search.perf_open_end.data, Performance.start_on)
            query = self.context.create_where(query, form_search.perf_close_start.data, form_search.perf_close_end.data, Performance.end_on)
            query = self.context.create_where(query, form_search.deal_open_start.data, form_search.deal_open_end.data, SalesSegment.start_at)
            query = self.context.create_where(query, form_search.deal_close_start.data, form_search.deal_close_end.data, SalesSegment.end_at)
            search_query = self.context.create_search_query(form_search)

            if form_search.lot_only.data:
                query = query.join(Event.lots)

        events = paginate.Page(
            query,
            page=int(self.request.params.get('page', 0)),
            items_per_page=50,
            url=PageURL_WebOb_Ex(self.request)
        )

        return {
            'form_search': form_search, 
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'events':events,
            'search_query':search_query,
            'h':EventHelper()
        }

    @view_config(route_name='events.show', renderer='altair.app.ticketing:templates/events/show.html', permission='event_viewer')
    def show(self):
        slave_session = get_db_session(self.request, name="slave")
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)
        cart_url = get_cart_url_builder(self.request).build(self.request, event)
        return {
            'event':event,
            'seat_stock_types':slave_session.query(StockType).filter_by(event_id=event_id, type=StockTypeEnum.Seat.v).order_by(StockType.display_order).all(),
            'non_seat_stock_types':slave_session.query(StockType).filter_by(event_id=event_id, type=StockTypeEnum.Other.v).order_by(StockType.display_order).all(),
            'cart_url': cart_url, 
            "cart_now_cart_url": get_cart_now_url_builder(self.request).build(self.request, cart_url, event.id), 
            'form':EventForm(),
            'form_performance':PerformanceForm(organization_id=self.context.user.organization_id),
            'form_stock_type':StockTypeForm(event_id=event_id),
            'form_stock_holder':StockHolderForm(organization_id=self.context.user.organization_id, event_id=event_id)
        }

    @view_config(route_name='events.new', request_method='GET', renderer='altair.app.ticketing:templates/events/edit.html')
    def new_get(self):
        f = EventForm(MultiDict(code=self.context.user.organization.code), organization_id=self.context.user.organization.id)
        return {
            'form':f,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='events.new', request_method='POST', renderer='altair.app.ticketing:templates/events/edit.html')
    def new_post(self):
        f = EventForm(self.request.POST, organization_id=self.context.user.organization.id)

        if f.validate():
            event = merge_session_with_post(
                Event(
                    organization_id=self.context.user.organization_id,
                    setting=EventSetting(
                        order_limit=f.order_limit.data,
                        max_quantity_per_user=f.max_quantity_per_user.data
                        )
                    ),
                f.data
                )
            event.save()

            self.request.session.flash(u'イベントを登録しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
                'route_name': u'登録',
                'route_path': self.request.path,
            }

    @view_config(route_name='events.edit', request_method='GET', renderer='altair.app.ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='GET', renderer='altair.app.ticketing:templates/events/edit.html')
    def edit_get(self):
        if self.request.matched_route.name == 'events.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.organization.id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(organization_id=self.context.organization.id, obj=event)
        f.order_limit.data = event.setting and event.setting.order_limit
        f.max_quantity_per_user.data = event.setting and event.setting.max_quantity_per_user

        if self.request.matched_route.name == 'events.copy':
            f.original_id.data = f.id.data
            f.id.data = None

        return {
            'form':f,
            'event':event,
            'route_name': route_name,
            'route_path': self.request.path,
        }

    @view_config(route_name='events.edit', request_method='POST', renderer='altair.app.ticketing:templates/events/edit.html')
    @view_config(route_name='events.copy', request_method='POST', renderer='altair.app.ticketing:templates/events/edit.html')
    def edit_post(self):
        if self.request.matched_route.name == 'events.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.organization.id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(self.request.POST, organization_id=self.context.organization.id)
        if f.validate():
            if self.request.matched_route.name == 'events.copy':
                event = merge_session_with_post(
                    Event(
                        organization_id=self.context.organization.id,
                        setting=EventSetting(
                            order_limit=f.order_limit.data,
                            max_quantity_per_user=f.max_quantity_per_user.data
                            )
                        ),
                    f.data
                    )
            else:
                event = merge_session_with_post(event, f.data)
                if event.setting is None:
                    event.setting = EventSetting()
                event.setting.order_limit = f.order_limit.data
                event.setting.max_quantity_per_user = f.max_quantity_per_user.data
            event.save()

            self.request.session.flash(u'イベントを保存しました')
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
        else:
            return {
                'form':f,
                'event':event,
                'route_name': route_name,
                'route_path': self.request.path,
            }

    @view_config(route_name='events.delete')
    def delete(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        try:
            core_api.delete_event(event)
            self.request.session.flash(u'イベントを削除しました')
        except Exception, e:
            self.request.session.flash(e.message)
            raise HTTPFound(location=route_path('events.show', self.request, event_id=event.id))

        return HTTPFound(location=route_path('events.index', self.request))

    @view_config(route_name='events.send')
    def send(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        try:
            organization = self.context.user.organization
            data = get_cms_data(self.request, organization, event)
        except Exception, e:
            logger.info("cms build data error: %s (event_id=%s)" % (e.message, event_id))
            self.request.session.flash(e.message)
            return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))

        communication_api = get_communication_api(self.request, CMSCommunicationApi)
        req = communication_api.create_connection('api/event/register', json.dumps(data))

        try:
            with contextlib.closing(urllib2.urlopen(req)) as res:
                if res.getcode() == HTTPCreated.code:
                    self.request.session.flash(u'イベントをCMSへ送信しました')
                    event.cms_send_at = datetime.now()
                    merge_and_flush(event)
                else:
                    raise Exception("cms sync http response error: reponse is not 302 (code:%s),  url=%s" % (res.getcode(),  res.url))
                    # raise Exception("cms sync http response error: reponse is not 302 (code:%s),  response=%s" % (res.getcode(), res.read()))
        except urllib2.HTTPError, e:
            logger.warn("cms sync http error: response code=(%s) event_id=%s url=%s method=%s %s" % (e.code, event_id, req.get_full_url(), req.get_method(), e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.code)
        except urllib2.URLError, e:
            logger.warn("cms sync url error: response status=(%s) event_id=%s url=%s method=%s %s" % (str(e.reason), event_id, req.get_full_url(), req.get_method(),  e))
            self.request.session.flash(u'イベント送信に失敗しました (%s)' % e.reason)
        except Exception, e:
            logger.error("cms sync error: %s" % (e.message))
            self.request.session.flash(u'イベント送信に失敗しました')

        return HTTPFound(location=route_path('events.show', self.request, event_id=event.id))
