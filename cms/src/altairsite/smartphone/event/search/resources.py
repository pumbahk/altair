# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altairsite.smartphone.common.searcher import EventSearcher
import webhelpers.paginate as paginate

class SearchResult(object):
    def __init__(self, num, start, end, page, page_end, query, events):
        self.num = num
        self.start = start
        self.end = end
        self.page = page
        self.page_end = page_end
        self.query = query
        self.events = events

class SearchPageResource(TopPageResource):
    def __init__(self, request):
        self.request = request

    def search_freeword(self, word):
        searcher = EventSearcher(request=self.request)
        qs = searcher.search_freeword(word=word)
        return qs

    def search_sale(self, sale):
        qs = ''
        return qs

    def create_result(self, qs, page, query, per):
        num = len(qs.all())
        start = page * per - per + 1
        end = page * per
        page_end = num / per + 1
        if num < end:
            end = num
        if num:
            events = self.paging(qs=qs, per=per, page=page)
        result =  SearchResult(num=num, start=start, end=end, page=page, page_end=page_end, query=query, events=events)
        return result

    def paging(self, qs, per, page):
        results = paginate.Page(qs.all(), page, per, url=paginate.PageURL_WebOb(self.request))
        return results
