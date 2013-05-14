# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altairsite.smartphone.common.searcher import EventSearcher
from altaircms.models import Genre
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error
from altaircms.genre.searcher import GenreSearcher
import webhelpers.paginate as paginate
from datetime import date

class SearchQuery(object):
    def __init__(self, word, sale):
        self.word = word
        self.sale = sale
    def to_string(self):
        str = u"フリーワード：" + self.word
        return str

class AreaSearchQuery(object):
    def __init__(self, area, genre_id, genre_label):
        self.area = area
        self.genre_id = genre_id
        self.word = genre_label
    def to_string(self):
        helper = SmartPhoneHelper()
        str = u"地域：" + helper.getRegionJapanese(self.area)
        if self.word:
             str = str + u', ジャンル:' + self.word
        return str

class DetailSearchQuery(object):
    def __init__(self, word, cond, genre, prefectures, sales_segment, event_open_info):
        self.word = word
        self.cond = cond
        self.genre = genre
        self.prefectures = prefectures
        self.sales_segment = sales_segment
        self.event_open_info = event_open_info
    def to_string(self):
        return u"フリーワード：" + self.word

class EventOpenInfo(object):
    def __init__(self, since_event_open, event_open):
        self.since_event_open = since_event_open
        self.event_open = event_open

class SearchResult(object):
    def __init__(self, query, num=0, start=0, end=0, page=1, page_end=1, events=None):
        self.query = query
        self.num = num
        self.start = start
        self.end = end
        self.page = page
        self.page_end = page_end
        self.events = events

class SearchPageResource(TopPageResource):
    def __init__(self, request):
        self.request = request

    # トップ画面、ジャンルの検索
    def search(self, query, page, per):
        qs = self.search_freeword(search_query=query, genre_label=None, cond=None)
        if qs:
            qs = self.search_sale(search_query=query, qs=qs)
        result = self.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # トップ画面、ジャンルのエリア検索
    def search_area(self, query, page, per):
        log_info("search_area", "start")
        qs = None
        if query.word:
            log_info("search_area", "genre=" + query.word)
            qs = self.search_freeword(search_query=query, genre_label=None, cond=None)
            if qs:
                log_info("search_area", "and search_area")
                qs = self._search_area(search_query=query, qs=qs)
        else:
            qs = self._search_area(search_query=query, qs=qs)
        result = self.create_result(qs=qs, page=page, query=query, per=per)
        log_info("search_area", "end")
        return result

    # 詳細検索
    def search_detail(self, query, page, per):
        qs = None

        # フリーワード、ジャンル
        if query.word:
            if query.genre:
                qs = self.search_freeword(search_query=query, genre_label=query.genre.label, cond=query.cond)
            else:
                qs = self.search_freeword(search_query=query, genre_label=None, cond=query.cond)

        if qs:
            qs = self._search_prefectures(search_query=query, qs=qs)
            qs = self._search_sales_segment(search_query=query, qs=qs)
            qs = self._search_event_open(search_query=query, qs=qs)

        result = self.create_result(qs=qs, page=page, query=query, per=per)
        return result

    def search_freeword(self, search_query, genre_label, cond):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(word=search_query.word, genre_label=genre_label, cond=cond)
        return qs

    def search_sale(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_sale(sale=search_query.sale, qs=qs)
        return qs

    def _search_area(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.get_events_from_area(area=search_query.area, qs=qs)
        return qs

    def _search_prefectures(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.get_events_from_prefectures(prefectures=search_query.prefectures, qs=qs)
        return qs

    def _search_sales_segment(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.get_events_from_salessegment(sales_segment=search_query.sales_segment, qs=qs)
        return qs

    def _search_event_open(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.get_events_from_start_on(event_open_info=search_query.event_open_info, qs=qs)
        return qs

    def create_result(self, qs, page, query, per):
        result = SearchResult(query)
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

    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id==id).first()
        return genre

    def paging(self, qs, per, page):
        results = paginate.Page(qs.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return results

    # 詳細検索フォーム生成
    def init_detail_search_form(self, form):
        form.genre_id.choices = self.create_genre_selectbox(self.request)
        form.year.choices, form.month.choices, form.day.choices = self.create_date_selectbox()
        form.since_year.choices, form.since_month.choices, form.since_day.choices = self.create_date_selectbox()

    def create_genre_selectbox(self, request):
        genre_searcher = GenreSearcher(request)
        genres = genre_searcher.root.children

        choices = []
        choices.append([0, u'選択なし'])
        for genre in genres:
            choices.append([genre.id, genre.label])
            for sub_genre in genre.children:
                choices.append([sub_genre.id, u"┗ " + sub_genre.label])
        return choices

    def create_date_selectbox(self):
        year_choices = []
        month_choices = []
        day_choices = []

        year_choices.append(['0', '-'])
        month_choices.append(['0', '-'])
        day_choices.append(['0', '-'])

        today = date.today()

        for year in range(today.year, today.year + 3):
            year_choices.append([str(year), str(year)])

        for month in range(1, 13):
            month_choices.append([str(month), str(month)])

        for day in range(1, 32):
            day_choices.append([str(day), str(day)])

        return year_choices, month_choices, day_choices

