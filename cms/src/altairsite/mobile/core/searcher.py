# -*- coding: utf-8 -*-
from altairsite.mobile.solr import helper
from pyramid.httpexceptions import HTTPNotFound
from altaircms.models import Performance, SalesSegmentGroup, SalesSegmentKind
from altaircms.event.models import Event
from altaircms.page.models import Page
from altaircms.models import Genre
from altairsite.mobile.core.const import get_prefecture
from altairsite.mobile.core.helper import exist_value
from altairsite.mobile.core.const import SalesEnum
from sqlalchemy import or_, and_, asc
from datetime import datetime, date, timedelta
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error

class EventSearcher(object):

    def __init__(self, request):
        self.request = request

    # 共通クエリ部分
    def _create_common_qs(self, where, qs=None):
        log_info("_create_common_qs", "start")
        if qs: # 絞り込み
            log_info("_create_common_qs", "and search")
            qs = qs.filter(where)
        else: # 新規検索
            log_info("_create_common_qs", "new search")
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
        log_info("_create_common_qs", "end")
        return qs

    # 検索文字列作成
    def create_search_freeword(self, form):
        log_info("create_search_freeword", "start")
        search_word = ""
        if exist_value(form.word.data):
            search_word = form.word.data

        if hasattr(form, "sub_genre"): # formが2種類入ってくるため
            if exist_value(form.sub_genre.data):
                subgenre = self.request.allowable(Genre).filter(Genre.id==form.sub_genre.data).first()
                search_word = search_word + " " + subgenre.label
            elif exist_value(form.genre.data):
                log_info("create_search_freeword", "sub_genre exist")
                genre = self.request.allowable(Genre).filter(Genre.id==form.genre.data).first()
                search_word = search_word + " " + genre.label
        elif exist_value(form.genre.data):
            subgenre = self.request.allowable(Genre).filter(Genre.id==form.genre.data).first()
            search_word = search_word + " " + subgenre.label
        log_info("create_search_freeword", "end")
        return search_word

    # フリーワード、ジャンル検索
    def get_events_from_freeword(self, form):
        log_info("get_events_from_freeword", "start")
        search_word = self.create_search_freeword(form)
        qs = None
        if search_word != "":
            try:
                log_info("FREEWORD_SEARCH", "SEARCH_WORD=" + search_word)
                events = helper.searchEvents(self.request, search_word)
                ids = self._create_ids(events)
                if len(ids) > 0:
                    qs = self._create_common_qs(where=Event.id.in_(ids))
            except Exception as e:
                log_error("get_events_from_freeword", str(e))
                qs = None
        log_info("get_events_from_freeword", "end")
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
    def get_events_from_area(self, form, qs=None):
        log_info("get_events_from_area", "start")
        if exist_value(form.area.data):
            log_info("get_events_from_area", "search start")
            prefectures = get_prefecture(form.area.data)
            log_info("get_events_from_area", "prefecture = " + str(prefectures))
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        log_info("get_events_from_area", "end")
        return qs

    # 発売状況
    def get_events_from_sale(self, form, qs=None):
        log_info("get_events_from_sale", "start")
        if form.sale.data == int(SalesEnum.ON_SALE):
            log_info("get_events_from_sale", "search start ON_SALE")
            qs = self._get_events_on_sale(form, qs)
        elif form.sale.data == int(SalesEnum.WEEK_SALE):
            log_info("get_events_from_sale", "search start WEEK_SALE")
            qs = self.get_events_week_sale(date.today(), None, qs)
        elif form.sale.data == int(SalesEnum.NEAR_SALE_END):
            log_info("get_events_from_sale", "search start NEAR_SALE_END")
            qs = self._get_events_near_sale_end(date.today(), 7, qs)
        elif form.sale.data == int(SalesEnum.SOON_ACT):
            log_info("get_events_from_sale", "search start SOON_ACT")
            qs = self._get_events_near_sale_end(date.today(), 7, qs)
            qs = self._create_common_qs(
                where=(
                    (date.today() < Performance.start_on) & \
                    (Performance.start_on < date.today() + timedelta(days=7))
                    ),
                qs=qs
                )
        elif form.sale.data == int(SalesEnum.ALL):
            pass
        log_info("get_events_from_sale", "end")
        return qs

    # 販売中
    def _get_events_on_sale(self, form, qs=None):
        log_info("_get_events_on_sale", "start")
        where = (datetime.now() <= Event.deal_close)
        qs = self._create_common_qs(where=where, qs=qs)
        log_info("_get_events_on_sale", "end")
        return qs

    # 今週発売検索(月曜日を週のはじめとする)
    def get_events_week_sale(self, today, offset=None, qs=None):
        log_info("get_events_week_sale", "start")
        start_day  = today + timedelta(days=offset or -today.weekday())
        where = (Event.deal_open >= start_day) & (Event.deal_open <= start_day+timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        log_info("get_events_week_sale", "end")
        return qs

    # 販売終了間近
    def _get_events_near_sale_end(self, today, N=7, qs=None):
        log_info("_get_events_near_sale_end", "start")
        limit_day = today + timedelta(days=N)
        where = (today <= Event.deal_close) & (Event.deal_close <= limit_day)
        qs = self._create_common_qs(where=where, qs=qs)
        log_info("_get_events_near_sale_end", "end")
        return qs

    # 公演日検索
    def get_events_from_start_on(self, form, qs=None):
        log_info("get_events_from_start_on", "start")
        if form.year.data == "0":
            # 全部ハイフンの場合
            log_info("get_events_from_start_on", "all hyphen")
            return qs

        log_info("get_events_from_start_on", "search start")
        since_open = datetime(
            int(form.since_year.data), int(form.since_month.data), int(form.since_day.data))
        open = datetime(
            int(form.year.data), int(form.month.data), int(form.day.data))
        where = (since_open <= Event.event_open) & (open >= Event.event_open)
        qs = self._create_common_qs(where=where, qs=qs)
        log_info("get_events_from_start_on", "search end")

        log_info("get_events_from_start_on", "end")
        return qs

    # 販売区分別
    def get_events_from_salessegment(self, form, qs=None):
        log_info("get_events_from_salessegment", "start")
        label = "一般発売"
        if form.sales_segment.data == 1:
            label = "一般先行"
        elif form.sales_segment.data == 2:
            label = "先行抽選"
        log_info("get_events_from_salessegment", "sales_segment = " + label)
        where = SalesSegmentKind.label == label
        qs = self._create_common_qs(where=where, qs=qs)
        log_info("get_events_from_salessegment", "end")
        return qs
