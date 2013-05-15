# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error
from altaircms.genre.searcher import GenreSearcher
from altairsite.smartphone.common.searcher import EventSearcher
from altaircms.models import Genre
from datetime import date

class SearchQuery(object):
    def __init__(self, word, genre, sale, sale_info):
        self.word = word
        self.genre = genre
        self.sale = sale
        self.sale_info = sale_info
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        query.append(u"フリーワード：" + self.word)
        if self.genre:
            query.append(u"ジャンル：" + self.genre.label)
        if self.sale:
            query.append(helper.get_sale_japanese(self.sale))
        if self.sale_info:
            if self.sale_info.sale_start:
                query.append(u"販売開始まで：" + str(self.sale.sale_start) + u"日")
            if self.sale_info.sale_end:
                query.append(u"販売終了まで：" + str(self.sale.sale_end) + u"日")
        return u"、".join(query)

    def create_parameter(self):
        parameter = "?word=" + self.word + "&sale=" + str(self.sale)
        if self.genre:
            parameter += "&genre_id=" + str(self.genre.id)
        if self.sale_info:
            if self.sale_info.sale_start:
                parameter += "&sale_start="
                parameter += str(self.sale_info.sale_start)
            if self.sale_info.sale_end:
                parameter += "&sale_end=" + str(self.sale_info.sale_end)
        return parameter

class AreaSearchQuery(object):
    def __init__(self, area, genre, genre_label):
        self.area = area
        self.genre = genre
        self.word = genre_label
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        query.append(u"地域：" + helper.get_area_japanese(self.area))
        if self.word:
            query.append(u"ジャンル：" + self.word)
        return u"、".join(query)
    def create_parameter(self):
        parameter = "?area=" + self.area
        if self.genre:
            parameter += "&genre_id=" + str(self.genre.id)
        return parameter

class DetailSearchQuery(object):
    def __init__(self, word, cond, genre, prefectures, sales_segment, event_open_info, sale_info, perf_info):
        self.word = word
        self.cond = cond
        self.genre = genre
        self.prefectures = prefectures
        self.sales_segment = sales_segment
        self.event_open_info = event_open_info
        self.sale_info = sale_info
        self.perf_info = perf_info
    def create_query(self):
        helper=SmartPhoneHelper()
        query = []
        query.append(u"フリーワード：" + self.word)
        if self.cond == "union":
            query.append(u"少なくとも１つを含む")
        else:
            query.append(u"全てを含む")
        if self.genre:
            query.append(u"ジャンル：" + self.genre.label)
        if self.sales_segment:
            query.append(helper.get_sales_segment_japanese(self.sales_segment))
        if self.event_open_info:
            if self.event_open_info.since_event_open and self.event_open_info.event_open:
                query.append(u"公演日：" + unicode(self.event_open_info.since_event_open) + u" 〜 " +  unicode(self.event_open_info.event_open))
        if self.sale_info:
            if self.sale_info.sale_start:
                query.append(u"販売開始まで：" + str(self.sale_info.sale_start) + u"日")
            if self.sale_info.sale_end:
                query.append(u"販売終了まで：" + str(self.sale_info.sale_end) + u"日")
        if self.perf_info:
            if self.perf_info.canceled:
                query.append(u"中止した公演")
            if self.perf_info.closed:
                query.append(u"販売終了した公演")
        if self.prefectures:
            first = False
            for pref in self.prefectures:
                if first:
                    query.append(helper.get_prefecture_japanese(pref))
                else:
                    query.append(u"県名：" + helper.get_prefecture_japanese(pref))
                    first = True
        return u"、".join(query)

class EventOpenInfo(object):
    def __init__(self, since_event_open, event_open):
        self.since_event_open = since_event_open
        self.event_open = event_open

class SaleInfo(object):
    def __init__(self, sale_start, sale_end):
        self.sale_start = sale_start
        self.sale_end = sale_end

class PerformanceInfo(object):
    def __init__(self, canceled, closed):
        self.canceled = canceled
        self.closed = closed

class SearchPageResource(TopPageResource):
    def __init__(self, request):
        self.request = request

    def get_genre(self, id):
        genre = self.request.allowable(Genre).filter(Genre.id==id).first()
        return genre

    # トップ画面・ジャンル画面検索
    def search(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(search_query=query, genre_label=None, cond=None)
        qs = searcher.search_sale(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # トップ画面、ジャンルのエリア検索
    def search_area(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = None
        if query.word:
            log_info("search_area", "genre=" + query.word)
            qs = searcher.search_freeword(search_query=query, genre_label=None, cond=None)
            qs = searcher.search_area(search_query=query, qs=qs)
        else:
            qs = searcher.search_area(search_query=query, qs=qs)

        qs = searcher.search_on_sale(qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 詳細検索
    def search_detail(self, query, page, per):
        searcher = EventSearcher(request=self.request)
        qs = None

        # フリーワード、ジャンル
        if query.word:
            if query.genre:
                qs = searcher.search_freeword(search_query=query, genre_label=query.genre.label, cond=query.cond)
            else:
                qs = searcher.search_freeword(search_query=query, genre_label=None, cond=query.cond)
        qs = searcher.search_prefectures(search_query=query, qs=qs)
        qs = searcher.search_sales_segment(search_query=query, qs=qs)
        qs = searcher.search_event_open(search_query=query, qs=qs)
        qs = searcher.search_near_sale_start(search_query=query, qs=qs)
        qs = searcher.search_near_sale_end(search_query=query, qs=qs)
        qs = searcher.search_perf(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result


    # 詳細検索フォーム生成
    def init_detail_search_form(self, form):
        form.genre_id.choices = self.create_genre_selectbox(self.request)
        form.year.choices, form.month.choices, form.day.choices = self.create_date_selectbox()
        form.since_year.choices, form.since_month.choices, form.since_day.choices = self.create_date_selectbox()
        form.sale_start.choices = self.create_choices(1, 32)
        form.sale_end.choices = self.create_choices(1, 32)

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

    def create_choices(self, start, end):
        choices = []
        choices.append(['', '-'])
        for value in range(start, end):
            choices.append([str(value), str(value)])
        return choices

    def create_date_selectbox(self):
        today = date.today()
        year_choices = self.create_choices(today.year, today.year + 3)
        month_choices = self.create_choices(1, 13)
        day_choices = self.create_choices(1, 32)
        return year_choices, month_choices, day_choices

