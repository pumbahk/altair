# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance, SalesSegmentGroup, SalesSegmentKind
from altaircms.event.models import Event
from altaircms.page.models import Page
from altaircms.models import Genre
from .const import get_prefectures
from altairsite.mobile.core.helper import exist_value
from altairsite.mobile.core.const import SalesEnum
from sqlalchemy import or_, and_, asc
from datetime import datetime, date, timedelta
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error
from altairsite.smartphone.common.solr import searchEvents

class EventSearcher(object):

    def __init__(self, request):
        self.request = request

    # フリーワード、ジャンル検索
    def search_freeword(self, word, genre_label, cond):
        log_info("search_freeword", "start")
        qs = None
        try:
            events = searchEvents(request=self.request, word=word, genre_label=genre_label, cond=cond)
            ids = self._create_ids(events)
            if len(ids) > 0:
                qs = self._create_common_qs(where=Event.id.in_(ids))
        except Exception as e:
            qs = None
        log_info("search_freeword", "end")
        return qs

    # 発売状況
    def search_sale(self, sale, qs):
        if sale == int(SalesEnum.ON_SALE):
            qs = self._get_events_on_sale(qs)
        elif sale == int(SalesEnum.WEEK_SALE):
            qs = self.get_events_week_sale(date.today(), None, qs)
        elif sale == int(SalesEnum.NEAR_SALE_END):
            qs = self._get_events_near_sale_end(date.today(), 7, qs)
        elif sale == int(SalesEnum.SOON_ACT):
            qs = self._get_events_near_act(qs)
        elif sale == int(SalesEnum.ALL):
            pass
        return qs

    # 販売中
    def _get_events_on_sale(self, qs=None):
        where = (datetime.now() <= Event.deal_close)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 今週発売検索(月曜日を週のはじめとする)
    def get_events_week_sale(self, today, offset=None, qs=None):
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (Event.deal_open >= start_day) & (Event.deal_open <= start_day+timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売終了間近
    def _get_events_near_sale_end(self, today, N=7, qs=None):
        if N:
            log_info("_get_events_near_sale_end", "near_sale_end = " + N)
            N = int(N)
            limit_day = today + timedelta(days=N)
            where = (today <= Event.deal_close) & (Event.deal_close <= limit_day)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # まもなく開演
    def _get_events_near_act(self, qs=None):
        qs = self._get_events_near_sale_end(date.today(), 7, qs)
        where = (date.today() < Performance.start_on) & \
                (Performance.start_on < date.today() + timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 共通クエリ部分
    def _create_common_qs(self, where, qs=None):
        if qs: # 絞り込み
            qs = qs.filter(where)
        else: # 新規検索
            qs = self.request.allowable(Event) \
                .join(Performance, Event.id == Performance.event_id) \
                .join(SalesSegmentGroup, SalesSegmentGroup.event_id == Event.id) \
                .join(SalesSegmentKind, SalesSegmentKind.id == SalesSegmentGroup.kind_id) \
                .join(Page, Page.event_id == Event.id) \
                .filter(Event.is_searchable == True) \
                .filter(Page.published == True) \
                .filter(Page.publish_begin < datetime.now()) \
                .filter((Page.publish_end==None) | (Page.publish_end > datetime.now())) \
                .filter(where)
        return qs

    # 取得イベントのIDリスト作成
    def _create_ids(self, events):
        log_info("_create_ids", "start")
        ids = []
        for event in events:
            ids.append(event.id)
        log_info("_create_ids", "event ID = %s" % str(ids))
        log_info("_create_ids", "end")
        return ids

    # 地域検索
    def get_events_from_area(self, area, qs=None):
        if area:
            prefectures = get_prefectures(area)
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 県名検索
    def get_events_from_prefectures(self, prefectures, qs=None):
        if prefectures:
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売区分別
    def get_events_from_salessegment(self, sales_segment, qs=None):
        label = "一般発売"
        if sales_segment == "precedence":
            label = "一般先行"
        elif sales_segment == "lottery":
            label = "先行抽選"
        log_info("get_events_from_salessegment", "sales_segment = " + label)
        where = SalesSegmentKind.label == label
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 公演日検索
    def get_events_from_start_on(self, event_open_info, qs=None):
        info = event_open_info
        if info.since_event_open and info.event_open:
            log_info("get_events_from_event_open", unicode(info.since_event_open) + u" 〜 " + unicode(info.event_open))
            where = (info.since_event_open <= Event.event_open) & (info.event_open >= Event.event_open)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

