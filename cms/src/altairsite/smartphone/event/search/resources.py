# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altairsite.smartphone.common.searcher import EventSearcher
from altaircms.models import Genre
from altairsite.smartphone.common.helper import SmartPhoneHelper
from altairsite.mobile.core.helper import log_debug, log_info, log_warn, log_exception, log_error
import webhelpers.paginate as paginate

class SearchQuery(object):
    def __init__(self, word, sale):
        self.word = word
        self.sale = sale
    def to_string(self):
        str = u"フリーワード：" + self.word
        return str

class AreaSearchQuery(object):
    def __init__(self, area, genre_label):
        self.area = area
        self.word = genre_label
    def to_string(self):
        helper = SmartPhoneHelper()
        str = u"地域：" + helper.getRegionJapanese(self.area)
        if self.word:
             str = str + u', ジャンル:' + self.word
        return str

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
        qs = self.search_freeword(search_query=query)
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
            qs = self.search_freeword(search_query=query)
            if qs:
                log_info("search_area", "and search_area")
                qs = self._search_area(search_query=query, qs=qs)
        else:
            qs = self._search_area(search_query=query, qs=qs)
        result = self.create_result(qs=qs, page=page, query=query, per=per)
        log_info("search_area", "end")
        return result

    def search_freeword(self, search_query):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(word=search_query.word)
        return qs

    def search_sale(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_sale(sale=search_query.sale, qs=qs)
        return qs

    def _search_area(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.get_events_from_area(area=search_query.area, qs=qs)
        return qs

    def create_result(self, qs, page, query, per):
        result = SearchResult(query)
        if qs:
            num = len(qs.all())
            start = page * per - per + 1
            end = page * per
            page_end = num / per + 1
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
