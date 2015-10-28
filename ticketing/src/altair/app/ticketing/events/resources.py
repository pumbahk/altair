# -*- coding: utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from datetime import timedelta
from altair.app.ticketing.core.models import Performance, SalesSegment
from sqlalchemy import or_

class EventAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(EventAdminResource, self).__init__(request)

    def need_join(self, query, form):
        if form.deal_range_start.data or form.deal_range_end.data or \
            form.deal_open_start.data or form.deal_open_end.data or \
            form.deal_close_start.data or form.deal_close_end.data:

            query = query.outerjoin(Performance)
            query = query.join(SalesSegment, Performance.id == SalesSegment.performance_id)

        elif form.performance_name_or_code.data or \
            form.perf_range_start.data or form.perf_range_end.data or \
            form.perf_open_start.data or form.perf_open_end.data or \
            form.perf_close_start.data or form.perf_close_end.data:

            query = query.outerjoin(Performance)
        return query

    def create_like_where(self, query, target, code, title):
        if target:
            pattern = '%' + target + '%'
            query = query.filter(or_(code.like(pattern), title.like(pattern)))
        return query

    def create_where(self, query, from_date, to_date, target):
        if from_date and to_date:
            where = (
                (from_date <= target) & (target <= to_date))
            query = query.filter(where)
        elif from_date:
            where = (from_date <= target)
            query = query.filter(where)
        elif to_date:
            where = (target <= to_date)
            query = query.filter(where)
        return query

    def create_range_where(self, query, from_date, to_date, from_target, to_target):
        if from_date and to_date:
            where = (
                (from_date <= from_target) & (from_target <= to_date) |
                (from_date <= to_target) & (to_target <= to_date) |
                (from_target <= from_date) & (to_date <= to_target))
            query = query.filter(where)
        elif from_date:
            where = (
                (from_date <= from_target) |
                (from_date <= from_target) & (from_target <= (from_date + timedelta(days=1))) & (to_target is None) |
                (from_target <= from_date) & (from_date <= to_target))
            query = query.filter(where)
        elif to_date:
            where = (
                (to_target <= to_date.data) |
                (from_target <= to_date.data) & (to_date.data <= to_target) |
                ((to_date + timedelta(days=-1)) <= from_target) & (from_target <= to_date) & (to_target is None))
            query = query.filter(where)
        return query

    def create_search_query(self, form):
        search_query = []
        if form.event_name_or_code.data:
            query = u"イベント名（コード）："
            query += form.event_name_or_code.data
            search_query.append(query)
        if form.performance_name_or_code.data:
            query = u"パフォーマンス名（コード）："
            query += form.performance_name_or_code.data
            search_query.append(query)
        if form.perf_range_start.data or form.perf_range_end.data:
            query = u"公演期間検索："
            str = self._get_str(form.perf_range_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.perf_range_end.data) or ""
            query += str
            search_query.append(query)
        if form.deal_range_start.data or form.deal_range_end.data:
            query = u"受付期間検索："
            str = self._get_str(form.deal_range_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.deal_range_end.data) or ""
            query += str
            search_query.append(query)
        if form.perf_open_start.data or form.perf_open_end.data:
            query = u"公演開始日検索："
            str = self._get_str(form.perf_open_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.perf_open_end.data) or ""
            query += str
            search_query.append(query)
        if form.perf_close_start.data or form.perf_close_end.data:
            query = u"公演終了日検索："
            str = self._get_str(form.perf_close_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.perf_close_end.data) or ""
            query += str
            search_query.append(query)
        if form.deal_open_start.data or form.deal_open_end.data:
            query = u"受付開始日検索："
            str = self._get_str(form.deal_open_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.deal_open_end.data) or ""
            query += str
            search_query.append(query)
        if form.deal_close_start.data or form.deal_close_end.data:
            query = u"受付終了日検索："
            str = self._get_str(form.deal_close_start.data) or ""
            query += str + u" 〜 "
            str = self._get_str(form.deal_close_end.data) or ""
            query += str
            search_query.append(query)
        if form.lot_only.data:
            search_query.append(u"抽選を含む")
        return ", ".join(search_query)

    def _get_str(self, target):
        if target:
            str = target.strftime("%Y/%m/%d")
            return str
        return target
