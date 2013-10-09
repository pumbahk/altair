# -*- coding:utf-8 -*-

""" カート画面の絞り込み切り替え
絞り込みキーと販売区分リスト
"""

from collections import OrderedDict
from zope.interface import implementer
from .interfaces import IPerformanceSelector
from .helpers import create_date_label, create_time_label, create_time_only_label

class _PerformanceSelector(object):
    def select_value(self, sales_segment):
        """
        販売区分からキーになる値を取り出す。
        """
        raise NotImplementedError()

    def sorter(self, a, b):
        """
        販売区分をソートするための関数。
        """
        return cmp(a.performance.display_order,
                   b.performance.display_order) or \
               cmp(a.performance.start_on,
                   b.performance.start_on) or \
               cmp(a.start_at,
                   b.start_at) or \
               cmp(a.performance.name,
                   b.performance.name)

    def build_key_to_sales_segments_map(self):
        key_to_sales_segments_map = {}
        for sales_segment in self.sales_segments:
            k = self.select_value(sales_segment)
            sales_segments_for_key = key_to_sales_segments_map.get(k)
            if sales_segments_for_key is None:
                sales_segments_for_key = key_to_sales_segments_map[k] = []
            sales_segments_for_key.append(sales_segment)
        # 販売区分の開始日時でソートする
        for k in key_to_sales_segments_map:
            key_to_sales_segments_map[k].sort(self.sorter)
        # さらにキーで束ねられたエントリを指定の条件でソート
        return sorted(key_to_sales_segments_map.items(), lambda a, b: self.sorter(a[1][0], b[1][0]))

    def sales_segment_to_dict(self, sales_segment):

        return dict(
            id=sales_segment.id,
            name=self._create_name(sales_segment),
            name_pc=self.time_label(sales_segment),
            name_mobile=self.time_label(sales_segment),
            name_smartphone=self.time_label(sales_segment),
            order_url=self.request.route_url(
                'cart.order',
                sales_segment_id=sales_segment.id),
            upper_limit=sales_segment.upper_limit,
            seat_types_url=self.request.route_url(
                'cart.seat_types2',
                performance_id=sales_segment.performance.id,
                sales_segment_id=sales_segment.id,
                event_id=self.context.event.id)
            )

    def _create_name(self, sales_segment):
        return self.time_label(sales_segment)

    def time_only_label(self, sales_segment):
        v = self.venue_label(sales_segment)
        t = create_time_only_label(sales_segment.performance.start_on, sales_segment.performance.end_on)
        if t:
            return t + " " + v
        else:
            return v

    def time_label(self, sales_segment):
        v = self.venue_label(sales_segment)
        t = create_time_label(sales_segment.performance.start_on, sales_segment.performance.end_on)
        return t + " " + v

    def venue_label(self, sales_segment):
        venue_format = u"{vname} {name}"
        return venue_format.format(
            name = sales_segment.name,
            vname = sales_segment.performance.venue.name)

@implementer(IPerformanceSelector)
class MatchUpPerformanceSelector(_PerformanceSelector):
    """ 対戦カード -> 会場 """

    label = u"対象試合"
    second_label = u"日付・会場"

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def select_value(self, sales_segment):
        """キーになる値"""
        return sales_segment.performance.name

    def __call__(self):
        selection = []
        key_to_sales_segments_map = self.build_key_to_sales_segments_map()
        for k, sales_segments in key_to_sales_segments_map:
            selection.append((k, [
                self.sales_segment_to_dict(sales_segment)
                for sales_segment in sales_segments
                ]))
        return selection

@implementer(IPerformanceSelector)
class DatePerformanceSelector(_PerformanceSelector):
    """ 日付 -> 会場 """

    label = u"開催日"
    second_label = u"日付・会場"

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def select_value(self, sales_segment):
        return create_date_label(sales_segment.performance.start_on, sales_segment.performance.end_on)

    def __call__(self):
        selection = []
        key_to_sales_segments_map = self.build_key_to_sales_segments_map()
        for k, sales_segments in key_to_sales_segments_map:
            selection.append((k, [
                self.sales_segment_to_dict(sales_segment)
                for sales_segment in sorted(sales_segments, key=lambda s: s.id)
                ]))
        return selection

    def sales_segment_to_dict(self, sales_segment):

        return dict(
            id=sales_segment.id,
            name=self._create_name(sales_segment),
            name_pc=self.time_only_label(sales_segment),
            name_mobile=self.time_label(sales_segment),
            name_smartphone=self.time_only_label(sales_segment),
            order_url=self.request.route_url(
                'cart.order',
                sales_segment_id=sales_segment.id),
            upper_limit=sales_segment.upper_limit,
            seat_types_url=self.request.route_url(
                'cart.seat_types2',
                performance_id=sales_segment.performance.id,
                sales_segment_id=sales_segment.id,
                event_id=self.context.event.id)
            )
