# -*- coding: utf-8 -*-
import logging
from cmsmobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance, SalesSegmentGroup, SalesSegmentKind
from altaircms.event.models import Event
from altaircms.models import Genre
from cmsmobile.core.const import get_prefecture
from cmsmobile.core.helper import exist_value
from cmsmobile.core.const import SalesEnum
from sqlalchemy import or_, and_, asc
from datetime import datetime, date, timedelta
from cmsmobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error

class EventSearcher(object):

    def __init__(self, request):
        self.request = request

    # 共通クエリ部分
    def _create_common_qs(self, where, qs=None):
        if qs: # 絞り込み
            qs = qs.filter(where)
        else: # 新規検索
            qs = self.request.allowable(Event) \
                .join(Performance, Event.id == Performance.event_id) \
                .join(SalesSegmentGroup, SalesSegmentGroup.event_id == Event.id) \
                .join(SalesSegmentKind, SalesSegmentKind.id == SalesSegmentGroup.kind_id) \
                .filter(Event.is_searchable == True) \
                .filter(where)
        return qs

    # 検索文字列作成
    def create_search_freeword(self, form):
        search_word = ""
        if exist_value(form.word.data):
            search_word = form.word.data

        if hasattr(form, "sub_genre"): # formが2種類入ってくるため
            if exist_value(form.sub_genre.data):
                genre = self.request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
                search_word = search_word + " " + genre.label
            elif exist_value(form.genre.data):
                subgenre = self.request.allowable(Genre).filter(Genre.id==form.genre.data).first()
                search_word = search_word + " " + subgenre.label
        elif exist_value(form.genre.data):
            subgenre = self.request.allowable(Genre).filter(Genre.id==form.genre.data).first()
            search_word = search_word + " " + subgenre.label
        return search_word

    # フリーワード、ジャンル検索
    def get_events_from_freeword(self, form):
        search_word = self.create_search_freeword(form)
        qs = None
        if search_word != "":
            try:
                log_info("FREEWORD_SEARCH", "SEARCH_WORD=" + search_word)
                events = helper.searchEvents(self.request, search_word)
                ids = self._create_ids(events)
                qs = self._create_common_qs(where=Event.id.in_(ids))
            except Exception, e:
                log_error("solr", "solr instance is not lunched.")
                raise HTTPNotFound
        return qs

    # 取得イベントのIDリスト作成
    def _create_ids(self, events):
        ids = []
        for event in events:
            ids.append(event.id)
        return ids

    # 地域検索
    def get_events_from_area(self, form, qs=None):
        if exist_value(form.area.data):
            prefectures = get_prefecture(form.area.data)
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 今週発売検索
    def get_events_week_sale(self, form, qs=None):
        if form.week_sale.data:
            qs = self._get_events_week_sale(date.today(), None, qs)
        return qs

    # まもなく開演
    def get_events_soon_act(self, form, qs=None):
        where = (date.today() < Performance.open_on) & \
                    (Performance.open_on < date.today() + timedelta(days=7))
        if form.soon_act.data:
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 発売状況
    def get_events_from_sale(self, form, qs=None):
        if form.sale.data == str(SalesEnum.ON_SALE):
            qs = self._get_events_on_sale(form, qs)
        elif form.sale.data == str(SalesEnum.WEEK_SALE):
            qs = self._get_events_week_sale(date.today(), None, qs)
        elif form.sale.data == str(SalesEnum.NEAR_SALE_END):
            qs = self._get_events_near_sale_end(date.today(), 7, qs)
        return qs

    # 販売中
    def _get_events_on_sale(self, form, qs=None):
        where = (datetime.now() >= Event.deal_open) & (datetime.now() <= Event.deal_close)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 今週発売検索(月曜日を週のはじめとする)
    def _get_events_week_sale(self, today, offset=None, qs=None):
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (Event.deal_open >= start_day) & (Event.deal_open <= start_day+timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売終了間近
    def _get_events_near_sale_end(self, today, N=7, qs=None):
        limit_day = today + timedelta(days=N)
        where = (Event.deal_open <= today) & (today <= Event.deal_close) & (Event.deal_close <= limit_day)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 公演日検索
    def get_events_from_start_on(self, form, qs=None):
        since_open = datetime(
            int(form.since_year.data), int(form.since_month.data), int(form.since_day.data))
        open = datetime(
            int(form.year.data), int(form.month.data), int(form.day.data))
        where = (since_open <= Event.event_open) & (open >= Event.event_open)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売区分別
    def get_events_from_salessegment(self, form, qs=None):
        label = "一般販売"
        if form.sales_segment.data:
            label = "一般先行"
        where = SalesSegmentKind.label == label
        qs = self._create_common_qs(where=where, qs=qs)
        return qs
