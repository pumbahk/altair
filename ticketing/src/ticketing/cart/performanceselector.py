# -*- coding:utf-8 -*-

""" カート画面の絞り込み切り替え
絞り込みキーと販売区分リスト
"""

from collections import OrderedDict
from zope.interface import implementer
from .interfaces import IPerformanceSelector

@implementer(IPerformanceSelector)
class MatchUpPerformanceSelector(object):
    """ 対戦カード -> 会場 """

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def __call__(self):
        performances = [ss.performance for ss in self.sales_segments]

        select_venues = OrderedDict()
        for p in performances:
            select_venues[p.name] = []

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
class DatePerformanceSelector(object):
    """ 日付け -> 会場 """

    def __init__(self, request):
        self.request = request
        self.context = request.context
        self.sales_segments = self.context.available_sales_segments

    def __call__(self):
        performances = [ss.performance for ss in self.sales_segments]

        select_venues = OrderedDict()
        for p in performances:
            d = p.start_on.strftime("%Y-%m-%d")
            select_venues[d] = []

        for sales_segment in self.sales_segments:
            performance = sales_segment.performance
            d = performance.start_on.strftime("%Y-%m-%d")

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
