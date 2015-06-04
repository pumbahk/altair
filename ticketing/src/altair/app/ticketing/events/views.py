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
from pyramid.renderers import render_to_response

from altair.sqlahelper import get_db_session
from altair.sqla import new_comparator

from altair.app.ticketing.models import merge_session_with_post, record_to_multidict, merge_and_flush
from altair.app.ticketing.views import BaseView
from altair.app.ticketing.fanstatic import with_bootstrap
from altair.app.ticketing.core.models import Event, EventSetting, Performance, PerformanceSetting, StockType, StockTypeEnum, SalesSegment
from altair.app.ticketing.core import api as core_api
from altair.app.ticketing.core.utils import PageURL_WebOb_Ex
from altair.app.ticketing.events.performances.forms import PerformanceForm
from altair.app.ticketing.events.stock_types.forms import StockTypeForm
from altair.app.ticketing.events.stock_holders.forms import StockHolderForm

from ..api.impl import get_communication_api
from ..api.impl import CMSCommunicationApi
from .api import get_cms_data, set_visible_event, set_invisible_event
from altair.app.ticketing.events.performances.api import set_visible_performance, set_invisible_performance
from .forms import EventForm, EventSearchForm, EventPublicForm
from .helpers import EventHelper
from altair.app.ticketing.carturl.api import get_cart_url_builder, get_cart_now_url_builder, get_agreement_cart_url_builder
logger = logging.getLogger()

@view_defaults(decorator=with_bootstrap, permission='event_editor')
class Events(BaseView):

    @view_config(route_name='events.visible', permission='event_viewer')
    def visible(self):
        set_visible_event(self.request)
        return HTTPFound(self.request.route_path("events.index"))

    @view_config(route_name='events.invisible', permission='event_viewer')
    def invisible(self):
        set_invisible_event(self.request)
        return HTTPFound(self.request.route_path("events.index"))

    @view_config(route_name='events.show.performances.visible', permission='event_viewer')
    def visible_performance(self):
        set_visible_performance(self.request)
        try:
            event_id = int(self.request.matchdict.get('event_id',0))
        except ValueError as e:
            return HTTPNotFound('event id not found')
        return HTTPFound(self.request.route_path("events.show", event_id=event_id))

    @view_config(route_name='events.show.performances.invisible', permission='event_viewer')
    def invisible_performance(self):
        set_invisible_performance(self.request)
        try:
            event_id = int(self.request.matchdict.get('event_id', 0))
        except ValueError as e:
            return HTTPNotFound('event id not found')
        return HTTPFound(self.request.route_path("events.show", event_id=event_id))

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
            .join(EventSetting, Event.id==EventSetting.event_id) \
            .filter(Event.organization_id==int(self.context.organization.id))

        # イベントの表示、非表示（クッキーで制御）
        from . import VISIBLE_EVENT_SESSION_KEY
        if not self.request.session.get(VISIBLE_EVENT_SESSION_KEY, None):
            query = query.filter(EventSetting.visible==True)

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
            'form':EventForm(context=self.context),
            'events':events,
            'search_query':search_query,
            'h':EventHelper()
        }

    @view_config(route_name='events.show', renderer='altair.app.ticketing:templates/events/show.html', permission='event_viewer')
    def show(self):
        slave_session = get_db_session(self.request, name="slave")
        try:
            event_id = int(self.request.matchdict.get('event_id', 0))
        except ValueError as e:
            return HTTPNotFound('event id not found')

        event = Event.get(event_id, organization_id=self.context.user.organization_id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)
        cart_url = get_cart_url_builder(self.request).build(self.request, event)
        agreement_url = get_agreement_cart_url_builder(self.request).build(self.request, event)
        performances = slave_session.query(Performance) \
            .join(PerformanceSetting, Performance.id == PerformanceSetting.performance_id) \
            .filter(Performance.event_id == event_id) \
            .order_by(Performance.display_order)

        from altair.app.ticketing.events.performances import VISIBLE_PERFORMANCE_SESSION_KEY
        if not self.request.session.get(VISIBLE_PERFORMANCE_SESSION_KEY, None):
            performances = performances.filter(PerformanceSetting.visible == True)
        performances = performances.all()

        return {
            'event':event,
            'performances':performances,
            'seat_stock_types':slave_session.query(StockType).filter_by(event_id=event_id, type=StockTypeEnum.Seat.v).order_by(StockType.display_order).all(),
            'non_seat_stock_types':slave_session.query(StockType).filter_by(event_id=event_id, type=StockTypeEnum.Other.v).order_by(StockType.display_order).all(),
            'cart_url': cart_url,
            'agreement_url': agreement_url,
            "cart_now_cart_url": get_cart_now_url_builder(self.request).build(self.request, cart_url, event.id),
            'form':EventForm(context=self.context),
            'form_performance':PerformanceForm(),
            'form_stock_type':StockTypeForm(event_id=event_id),
            'form_stock_holder':StockHolderForm(organization_id=self.context.user.organization_id, event_id=event_id)
        }

    @view_config(route_name='events.new', request_method='GET', renderer='altair.app.ticketing:templates/events/edit.html')
    def new_get(self):
        f = EventForm(MultiDict(code=self.context.user.organization.code, visible=True), context=self.context)
        return {
            'form':f,
            'route_name': u'登録',
            'route_path': self.request.path,
        }

    @view_config(route_name='events.new', request_method='POST', renderer='altair.app.ticketing:templates/events/edit.html')
    def new_post(self):
        f = EventForm(self.request.POST, context=self.context)

        if f.validate():
            event = merge_session_with_post(
                Event(
                    organization_id=self.context.user.organization_id,
                    setting=EventSetting(
                        order_limit=f.order_limit.data,
                        max_quantity_per_user=f.max_quantity_per_user.data,
                        middle_stock_threshold=f.middle_stock_threshold.data,
                        middle_stock_threshold_percent=f.middle_stock_threshold_percent.data,
                        cart_setting_id=f.cart_setting_id.data,
                        visible=f.visible.data
                        # performance_selector=f.get_performance_selector(),
                        # performance_selector_label1_override=f.performance_selector_label1_override.data,
                        # performance_selector_label2_override=f.performance_selector_label2_override.data,
                        )
                    ),
                f.data,
                # excludes={'performance_selector',
                #           'performance_selector_label1_override',
                #           'performance_selector_label2_override',
                #           },
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
    @view_config(route_name='events.copy', request_method='GET', renderer='altair.app.ticketing:templates/events/copy.html')
    def edit_get(self):
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.organization.id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(context=self.context, obj=event)
        f.order_limit.data = event.setting and event.setting.order_limit
        f.max_quantity_per_user.data = event.setting and event.setting.max_quantity_per_user
        f.middle_stock_threshold.data = event.setting and event.setting.middle_stock_threshold
        f.middle_stock_threshold_percent.data = event.setting and event.setting.middle_stock_threshold_percent
        f.cart_setting_id.data = event.setting and event.setting.cart_setting_id
        f.visible.data = event.setting and event.setting.visible
        if self.request.matched_route.name == 'events.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
            # コピー時は、必ず表示
            f.visible.data = True

        # f.performance_selector.data = (event.setting.performance_selector or '') if event.setting else ''
        # f.performance_selector_label1_override.data = event.setting.performance_selector_label1_override if event.setting else ''
        # f.performance_selector_label2_override.data = event.setting.performance_selector_label2_override if event.setting else ''

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
    @view_config(route_name='events.copy', request_method='POST', renderer='altair.app.ticketing:templates/events/copy.html')
    def edit_post(self):
        if self.request.matched_route.name == 'events.edit':
            route_name = u'編集'
        else:
            route_name = u'コピー'
        event_id = int(self.request.matchdict.get('event_id', 0))
        event = Event.get(event_id, organization_id=self.context.organization.id)
        if event is None:
            return HTTPNotFound('event id %d is not found' % event_id)

        f = EventForm(self.request.POST, context=self.context)
        if f.validate():
            if self.request.matched_route.name == 'events.copy':
                event = merge_session_with_post(
                    Event(
                        organization_id=self.context.organization.id,
                        setting=EventSetting(
                            order_limit=f.order_limit.data,
                            max_quantity_per_user=f.max_quantity_per_user.data,
                            middle_stock_threshold=f.middle_stock_threshold.data,
                            middle_stock_threshold_percent=f.middle_stock_threshold_percent.data,
                            cart_setting_id=f.cart_setting_id.data,
                            visible=True
                            # performance_selector=f.get_performance_selector(),
                            # performance_selector_label1_override=f.performance_selector_label1_override.data,
                            # performance_selector_label2_override=f.performance_selector_label2_override.data,
                            ),
                        ),
                    f.data,
                    # excludes={'performance_selector',
                    #           'performance_selector_label1_override',
                    #           'performance_selector_label2_override',
                    #           },
                    )
            else:
                event = merge_session_with_post(event, f.data,
                    # excludes={'performance_selector',
                    #           'performance_selector_label1_override',
                    #           'performance_selector_label2_override',
                    #           },
                )
                if event.setting is None:
                    event.setting = EventSetting()
                event.setting.order_limit = f.order_limit.data
                event.setting.max_quantity_per_user = f.max_quantity_per_user.data
                event.setting.middle_stock_threshold = f.middle_stock_threshold.data
                event.setting.middle_stock_threshold_percent = f.middle_stock_threshold_percent.data
                event.setting.visible = f.visible.data
                if f.cart_setting_id.data is not None:
                    event.setting.cart_setting_id = f.cart_setting_id.data
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

    @view_config(route_name='events.open', request_method='GET',renderer='altair.app.ticketing:templates/events/_form_open.html')
    def open_get(self):
        if 'event_id' not in self.request.matchdict or 'public' not in self.request.matchdict:
            return HTTPNotFound('events.open GET matchdict parameter Fraud')

        f = EventPublicForm()
        f.event_id.data = self.request.matchdict['event_id']
        f.public.data = self.request.matchdict['public']
        f.public.data = 1 if f.public.data == 'true' else 0

        slave_session = get_db_session(self.request, name="slave")
        event = slave_session.query(Event).filter_by(id=f.event_id.data).first()

        if not event:
            return HTTPNotFound('events.open GET event not found')

        return {
            'form':f,
            'event':event,
        }

    @view_config(route_name='events.open', request_method='POST',renderer='altair.app.ticketing:templates/events/_form_open.html')
    def open_post(self):
        if 'event_id' not in self.request.matchdict or 'public' not in self.request.matchdict:
            return HTTPNotFound('events.open POST matchdict parameter Fraud')

        f = EventPublicForm()
        f.event_id.data = self.request.matchdict['event_id']
        f.public.data = self.request.matchdict['public']
        f.public.data = True if f.public.data == '1' else False

        if f.validate():
            event = Event.get(f.event_id.data, organization_id=self.context.user.organization_id)

            if not event:
                return HTTPNotFound('events.open POST event not found')

            for perf in event.performances:
                perf.public = f.public.data
                perf.save()
                logger.info("performance public changed %s (event_id=%s)" % (f.public.data, event.id))

            if len(event.performances):
                if f.public.data:
                    self.request.session.flash(u'パフォーマンスを全て公開しました')
                else:
                    self.request.session.flash(u'パフォーマンスを全て非公開にしました')
            else:
                self.request.session.flash(u'パフォーマンスがありません')

            return render_to_response('altair.app.ticketing:templates/refresh.html', {}, request=self.request)

        return {
            'form':f,
        }
