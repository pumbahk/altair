# -*- coding:utf-8 -*-
from altairsite.smartphone.event.search.resources import SearchPageResource
from altairsite.smartphone.common.const import SalesEnum
from altairsite.smartphone.event.search.resources import SearchQuery
from altairsite.smartphone.common.searcher import EventSearcher

class GenrePageResource(SearchPageResource):

    # 今週発売
    def search_week(self, genre_label, page, per):
        searcher = EventSearcher(request=self.request)
        query = SearchQuery(genre_label, SalesEnum.WEEK_SALE.v)
        qs = searcher.search_freeword(search_query=query, genre_label=genre_label, cond=None)
        if qs:
            qs = searcher.search_week_sale(offset=None, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 販売終了間近
    def search_near_end(self, genre_label, page, per):
        searcher = EventSearcher(request=self.request)
        query = SearchQuery(genre_label, SalesEnum.NEAR_SALE_END.v)
        qs = searcher.search_freeword(search_query=query, genre_label=genre_label, cond=None)
        if qs:
            qs = searcher.search_near_sale_end(N=7, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result
