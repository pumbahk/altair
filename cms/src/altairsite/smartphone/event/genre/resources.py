# -*- coding:utf-8 -*-
from altairsite.smartphone.event.search.resources import SearchPageResource
from altairsite.smartphone.common.const import SalesEnum
from altairsite.smartphone.event.search.resources import SearchQuery

class GenrePageResource(SearchPageResource):

    def search(self, query, page, per):
        qs = self.search_sale(search_query=query, qs=None)
        result = self.create_result(qs=qs, page=page, query=query, per=per)
        return result

    def search_week(self, genre_label, page, per):
        # 今週発売
        query = SearchQuery(genre_label, SalesEnum.WEEK_SALE.v)
        week_result = self.search(query, page, per)
        return week_result

    def search_near_end(self, genre_label, page, per):
        # 販売終了間近
        query = SearchQuery(genre_label, SalesEnum.NEAR_SALE_END.v)
        near_end_result = self.search(query, page, per)
        return near_end_result
