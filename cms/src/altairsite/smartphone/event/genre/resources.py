# -*- coding:utf-8 -*-
from altairsite.smartphone.event.search.resources import SearchPageResource
from altairsite.smartphone.common.const import SalesEnum
from altairsite.smartphone.event.search.resources import SearchQuery, SaleInfo
from altairsite.smartphone.common.searcher import EventSearcher

class GenrePageResource(SearchPageResource):

    # ２回全文検索しない
    def load_freeword(self, search_query):
        qs = None
        if getattr(self.request, "genre_freeword", None):
            qs = self.request.genre_freeword
        else:
            searcher = EventSearcher(request=self.request)
            qs = searcher.search_freeword(search_query=search_query, genre_label=search_query.genre_label, cond=None)
            self.request.genre_freeword = qs
        return qs

    # 今週発売
    def search_week(self, genre_label, page, per):
        searcher = EventSearcher(request=self.request)
        query = SearchQuery(None, genre_label, SalesEnum.WEEK_SALE.v, None)
        qs = self.load_freeword(search_query=query)
        qs = searcher.search_week_sale(offset=None, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result

    # 販売終了間近
    def search_near_end(self, genre_label, page, per):
        searcher = EventSearcher(request=self.request)
        sale_info = SaleInfo(sale_start=None, sale_end=7)
        query = SearchQuery(None, genre_label, SalesEnum.NEAR_SALE_END.v, sale_info)
        qs = self.load_freeword(search_query=query)
        qs = searcher.search_near_sale_end(search_query=query, qs=qs)
        result = searcher.create_result(qs=qs, page=page, query=query, per=per)
        return result
