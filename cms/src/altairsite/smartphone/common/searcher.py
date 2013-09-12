# -*- coding: utf-8 -*-
from .solr import searchEvents
from .const import get_prefectures, SalesEnum
from altaircms.page.models import Page
from altaircms.event.models import Event
from altairsite.mobile.core.helper import log_info
from altaircms.models import Performance, SalesSegmentGroup, SalesSegmentKind

import webhelpers.paginate as paginate
from datetime import datetime, date, timedelta
from altaircms.datelib import get_now, get_today

class SearchResult(object):
    def __init__(self, query, num=0, start=0, end=0, page=1, page_end=1, events=None):
        self.query = query
        self.num = num
        self.start = start
        self.end = end
        self.page = page
        self.page_end = page_end
        self.events = events

class EventSearcher(object):

    def __init__(self, request):
        self.request = request

    # フリーワード、ジャンル検索
    def search_freeword(self, search_query, genre_label, cond):
        qs = None
        try:
            events = searchEvents(request=self.request, word=search_query.word, genre_label=genre_label, cond=cond)
            ids = self._create_ids(events)
            if len(ids) > 0:
                qs = self._create_common_qs(where=Event.id.in_(ids))
        except Exception as e:
            qs = None
        return qs

    def _create_ids(self, events):
        ids = []
        for event in events:
            ids.append(event.id)
        log_info("_create_ids", "event ID = %s" % str(ids))
        return ids

    # 発売状況
    def search_sale(self, search_query, qs=None):
        sale = search_query.sale
        if sale == SalesEnum.ON_SALE.v:
            qs = self.search_event_in_session(qs)
        elif sale == SalesEnum.GENRE.v:
            qs = self.search_event_in_session(qs)
        elif sale == SalesEnum.WEEK_SALE.v:
            qs = self.search_week_sale(None, qs)
        elif sale == SalesEnum.NEAR_SALE_END.v:
            qs = self.search_near_sale_end(search_query, qs=qs)
        elif sale == SalesEnum.SOON_ACT.v:
            qs = self.search_near_act(qs)
        elif sale == SalesEnum.ALL.v:
            pass
        return qs

    # 今週発売検索(月曜日を週のはじめとする)
    def search_week_sale(self, offset=None, qs=None):
        today = get_today(self.request)
        start_day = today + timedelta(days=offset or -today.weekday())
        where = (Event.deal_open >= start_day) & (Event.deal_open <= start_day+timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # まもなく開演
    def search_near_act(self, qs=None):
        where = (get_today(self.request) < Performance.start_on) & \
                (Performance.start_on < get_today(self.request) + timedelta(days=7))
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売終了間近
    def search_near_sale_end(self, search_query, qs=None):
        sale_end = search_query.sale_info.sale_end
        if sale_end:
            log_info("search_near_sale_end", "near_sale_end = " + str(sale_end))
            today = get_today(self.request)
            sale_end = int(sale_end)
            limit_day = today + timedelta(days=sale_end)
            where = (today <= Event.deal_close) & (Event.deal_close <= limit_day)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 地域検索
    def search_area(self, search_query, qs=None):
        if search_query.area:
            prefectures = get_prefectures(search_query.area)
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 県名検索
    def search_prefectures(self, search_query, qs=None):
        prefectures = search_query.get_prefectures()
        if prefectures:
            log_info("search_prefectures", " ,".join(prefectures))
            where = Performance.prefecture.in_(prefectures)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売区分別
    def search_sales_segment(self, search_query, qs=None):
        labels = []
        for segment in search_query.sales_segment:
            if segment == "normal":
                labels.append("一般発売")
            elif segment == "precedence":
                labels.append("一般発売")
            elif segment == "lottery":
                labels.append("先行抽選")

        if labels:
            log_info("search_sales_segment", "sales_segment = " + ", ".join(labels))
            where=SalesSegmentKind.label.in_(labels)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 公演日検索
    def search_event_open(self, search_query, qs=None):
        info = search_query.event_open_info
        if info.since_event_open and info.event_open:
            where = (
                (info.since_event_open <= Event.event_open) & (info.event_open >= Event.event_open) |
                (info.since_event_open <= Event.event_close) & (info.event_open >= Event.event_close) |
                (Event.event_open <= info.since_event_open) & (Event.event_close >= info.event_open)
            )
            qs = self._create_common_qs(where=where, qs=qs)
        elif info.since_event_open:
            where = (
                (Event.event_open <= info.since_event_open) & (Event.event_close  >= info.since_event_open) |
                (Event.event_open >= info.since_event_open)
            )
            qs = self._create_common_qs(where=where, qs=qs)
        elif info.event_open:
            where = (
                (Event.event_open <= info.event_open) & (Event.event_close  >= info.event_open) |
                (Event.event_close <= info.event_open)
            )
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売開始まで
    def search_near_sale_start(self, search_query, qs=None):
        sale_start = search_query.sale_info.sale_start
        if sale_start:
            log_info("search_near_sale_start", "near_sale_start = " + str(sale_start))
            today = get_today(self.request)
            sale_start = int(sale_start)
            sale_day = today + timedelta(days=sale_start)
            where = (Event.deal_open <= sale_day) & (Event.deal_open >= today)
            qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 公演状態による検索
    def search_perf(self, search_query, qs=None):
        info = search_query.perf_info
        if info.canceled:
            qs = self.search_canceled(qs=qs)
        if info.closed:
            qs = self.search_closed(qs=qs)
        if not info.canceled and not info.closed:
                qs = self.search_event_in_session(qs=qs)
        return qs

    # 公演が終了しているかどうか
    def search_event_in_session(self, qs=None):
        where = (get_now(self.request) <= Event.event_close)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 中止した公演
    def search_canceled(self, qs=None):
        where = (Performance.canceld == True)
        qs = self._create_common_qs(where=where, qs=qs)
        return qs

    # 販売終了した公演
    def search_closed(self, qs=None):
        where = (get_now(self.request) > Event.deal_close)
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
                .filter(Page.publish_begin < get_now(self.request)) \
                .filter((Page.publish_end==None) | (Page.publish_end > get_now(self.request))) \
                .filter(where)
        return qs

    # 検索結果の作成
    def create_result(self, qs, page, query, per):
        result = SearchResult(query)
        page = int(page)
        if qs:
            num = len(qs.all())
            start = page * per - per + 1
            end = page * per
            page_end = num / per + 1
            if num % per == 0:
                page_end = num / per

            if num < end:
                end = num

            if num:
                events = self.paging(qs=qs, per=per, page=page)
                result = SearchResult(query=query, num=num, start=start, end=end, page=page, page_end=page_end, events=events)
        return result

    def paging(self, qs, per, page):
        results = paginate.Page(qs.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return results

class SimpleEventSearcher(EventSearcher):
    # 共通クエリ部分
    def _create_common_qs(self, where, qs=None):
        if qs: # 絞り込み
            qs = qs.filter(where)
        else: # 新規検索
            qs = self.request.allowable(Event) \
                .join(Page, Page.event_id == Event.id) \
                .filter(Event.is_searchable == True) \
                .filter(Page.published == True) \
                .filter(Page.publish_begin < get_now(self.request)) \
                .filter((Page.publish_end==None) | (Page.publish_end > get_now(self.request))) \
                .filter(where)
        return qs

class PrefectureEventSearcher(EventSearcher):
    # 共通クエリ部分
    def _create_common_qs(self, where, qs=None):
        if qs: # 絞り込み
            qs = qs.filter(where)
        else: # 新規検索
            qs = self.request.allowable(Event) \
                .join(Performance, Event.id == Performance.event_id) \
                .join(Page, Page.event_id == Event.id) \
                .filter(Event.is_searchable == True) \
                .filter(Page.published == True) \
                .filter(Page.publish_begin < get_now(self.request)) \
                .filter((Page.publish_end==None) | (Page.publish_end > get_now(self.request))) \
                .filter(where)
        return qs
