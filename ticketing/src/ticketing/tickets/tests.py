# encoding: utf-8

from unittest import TestCase
from datetime import datetime



class TicketsUtilsTest(TestCase):
    def build_seat_fixture(self):
        from ..core.models import Organization, Event, Performance, StockType, StockTypeEnum, StockHolder, Stock, StockStatus, Venue, Seat, SeatStatus, SeatStatusEnum
        organization = Organization(
            name=u'組織名',
            code=u'RT'
            )
        event = Event(
            code=u'RTTST',
            title=u'イベント名',
            abbreviated_title=u'イベント名略称',
            organization=organization
            )
        performance = Performance(
            event=event,
            name=u'パフォーマンス名',
            code=u'RTTST0000000',
            open_on=datetime(2012, 12, 31, 10, 1, 2),
            start_on=datetime(2012, 12, 31, 11, 3, 4),
            end_on=datetime(2012, 12, 31, 12, 5, 6)
            )
        stock_type = StockType(
            name=u'S席',
            type=StockTypeEnum.Seat.v,
            display_order=0,
            quantity_only=0,
            event=event
            )
        stock_holder = StockHolder(
            name=u'stock_holder'
            )
        stock = Stock(
            performance=performance,
            stock_type=stock_type,
            stock_holder=stock_holder,
            quantity=100,
            stock_status=StockStatus(
                quantity=98
                )
            )
        venue = Venue(
            performance=performance,
            name=u'会場名',
            sub_name=u'サブ会場名'
            )
        seat = Seat(
            l0_id=u'l0_id',
            name=u'seat_name',
            seat_no=u'seat_no',
            stock=stock,
            status_=SeatStatus(status=SeatStatusEnum.Ordered.v),
            venue=venue,
            attributes={
                u'a': u'b',
                u'c': u'd'
                }
            )
        return seat 

    def test_build_dict_from_seat(self):
        from .utils import build_dict_from_seat

        seat = self.build_seat_fixture()
        out = build_dict_from_seat(seat, None)
        expected = {
            u"organization": {
                u"name": u"組織名",
                u"code": u"RT"
                },
            u"event": {
                u"code": u"RTTST",
                u"title": u"イベント名",
                u"abbreviated_title": u"イベント名略称"
                },
            u"performance": {
                u"name": u"パフォーマンス名",
                u"code": u"RTTST0000000",
                u"open_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 10, u"minute": 1, u"second": 2
                    },
                u"start_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 11, u"minute": 3, u"second": 4
                    },
                u"end_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 12, u"minute": 5, u"second": 6
                    }
                },
            u"venue": {
                u"name": u"会場名",
                u"sub_name": u"サブ会場名"
                },
            u"stock": {
                u"quantity": 100
                },
            u"stockStatus": {
                u"quantity": 98,
                },
            u"stockHolder": {
                u"name": u"stock_holder"
                },
            u"stockType": {
                u"name": u"S席",
                u"type": 0,
                u"display_order": 0,
                u"quantity_only": 0
                },
            u"seat": {
                u"l0_id": u"l0_id",
                u"name": u"seat_name",
                u"seat_no": u"seat_no"
                },
            u"イベント名": u"イベント名",
            u"パフォーマンス名": u"パフォーマンス名",
            u"対戦名": u"パフォーマンス名",
            u"会場名": u"会場名",
            u"公演コード": u"RTTST0000000",
            u"開催日": u"2012年 12月 31日",
            u"開場時刻": u"10時 01分",
            u"開始時刻": u"11時 03分",
            u"終了時刻": u"12時 05分",
            u"席種名": u"S席",
            u"席番": u"seat_name",
            u"発券番号": None 
            }
        for k in expected:
            self.assertEqual(expected[k], out[k], k.encode('utf-8'))

