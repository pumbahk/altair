# -*- coding:utf-8 -*-

""" カート画面の絞り込み切り替え
絞り込みキーと販売区分リスト
"""

from collections import OrderedDict
from zope.interface import implementer
from .interfaces import IPerformanceSelector


class _PerformanceSelector(object):

    @property
    def selection(self):
        performances = sorted(list(set([ss.performance for ss in self.sales_segments])), 
                              key=lambda p: p.start_on)
        return [self.select_value(p) for p in performances]


@implementer(IPerformanceSelector)
class MatchUpPerformanceSelector(_PerformanceSelector):
    """ 対戦カード -> 会場 """

    label = u"対象試合"
    second_label = u"日付・会場"

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def select_value(self, performance):
        return performance.name

    def __call__(self):

        select_venues = OrderedDict()
        for v in self.selection:
            select_venues[v] = []

        for sales_segment in self.sales_segments:
            performance = sales_segment.performance
            pname = performance.name
            select_venues[pname].append(dict(
                id=performance.id,
                name=u'{start:%Y-%m-%d %H:%M}開始 {vname} {name}'.format(name=sales_segment.name, start=performance.start_on, vname=performance.venue.name),
                order_url=self.request.route_url("cart.order", sales_segment_id=sales_segment.id),
                upper_limit=sales_segment.upper_limit,
                seat_types_url=self.request.route_url('cart.seat_types',
                    performance_id=performance.id,
                    sales_segment_id=sales_segment.id,
                    event_id=self.context.event.id)))

        return select_venues


@implementer(IPerformanceSelector)
class DatePerformanceSelector(_PerformanceSelector):
    """ 日付け -> 会場 """

    label = u"開催日"
    second_label = u"会場"

    date_format = u"{0.year:04}年{0.month:02}月{0.day:02}日"

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def select_value(self, performance):
        #return performance.start_on.strftime(self.date_format)
        return self.date_format.format(performance.start_on)

    @property
    def selection(self):
        performances = [ss.performance for ss in self.sales_segments]
        return [self.select_value(p) for p in performances]

    def __call__(self):

        select_venues = OrderedDict()
        for v in self.selection:
            select_venues[v] = []

        for sales_segment in self.sales_segments:
            performance = sales_segment.performance
            #d = performance.start_on.strftime(self.date_format)
            d = self.select_value(performance)

            select_venues[d].append(dict(
                id=performance.id,
                name=u'{start:%Y-%m-%d %H:%M}開始 {vname} {name}'.format(name=sales_segment.name, start=performance.start_on, vname=performance.venue.name),
                order_url=self.request.route_url("cart.order", sales_segment_id=sales_segment.id),
                upper_limit=sales_segment.upper_limit,
                seat_types_url=self.request.route_url('cart.seat_types',
                    performance_id=performance.id,
                    sales_segment_id=sales_segment.id,
                    event_id=self.context.event.id)))

        return select_venues
