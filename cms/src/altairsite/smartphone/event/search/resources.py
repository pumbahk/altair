# -*- coding:utf-8 -*-
from altairsite.smartphone.event.genre.resources import GenrePageResource
from altairsite.smartphone.common.searcher import EventSearcher
from altairsite.smartphone.common.const import SalesEnum
import webhelpers.paginate as paginate

class SearchQuery(object):
    def __init__(self, word, sale):
        self.word = word
        self.sale = sale
    def to_string(self):
        str = u"フリーワード：" + self.word
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

class SearchPageResource(GenrePageResource):
    def __init__(self, request):
        self.request = request

    def search(self, query, page, per):
        qs = self.search_freeword(search_query=query)
        if qs:
            qs = self.search_sale(search_query=query, qs=qs)
        result = self.create_result(qs=qs, page=page, query=query, per=per)
        return result

    def search_freeword(self, search_query):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(word=search_query.word)
        return qs

    def search_sale(self, search_query, qs):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_sale(sale=search_query.sale, qs=qs)
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

    def paging(self, qs, per, page):
        results = paginate.Page(qs.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return results
