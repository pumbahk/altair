# encoding: utf-8

from unittest import TestCase
from datetime import datetime
from lxml import etree

class TicketsUtilsTest(TestCase):
    def build_seat_fixture(self):
        from ticketing.core.models import Organization, Event, Performance, StockType, StockTypeEnum, StockHolder, Stock, StockStatus, Venue, Seat, SeatStatus, SeatStatusEnum
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
            end_on=None, 
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
        from ticketing.tickets.utils import build_dict_from_seat

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
                    u"hour": 10, u"minute": 1, u"second": 2, 
                    u"weekday": 0, 
                    },
                u"start_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 11, u"minute": 3, u"second": 4, 
                    u"weekday": 0, 
                    },
                u"end_on": None, 
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
            u"開催日": u"2012年 12月 31日 (月)",
            u"開場時刻": u"10時 01分",
            u"開始時刻": u"11時 03分",
            u"終了時刻": u"",
            u"席種名": u"S席",
            u"席番": u"seat_name",
            u"発券番号": None 
            }
        for k in expected:
            self.assertEqual(expected[k], out[k], k.encode('utf-8'))

class TicketsCleanerTest(TestCase):
    def testTransformApplier(self):
        from ticketing.tickets.cleaner import TransformApplier
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="10" height="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(10, float(elem.get(u'x')))
        self.assertEqual(20, float(elem.get(u'y')))
        self.assertEqual(20, float(elem.get(u'width')))
        self.assertEqual(20, float(elem.get(u'height')))

        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(30, float(elem.get(u'cx')))
        self.assertEqual(40, float(elem.get(u'cy')))
        self.assertEqual(10, float(elem.get(u'r')))

        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><line x1="20" y1="10" x2="0" y2="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(40, float(elem.get(u'x1')))
        self.assertEqual(50, float(elem.get(u'y1')))
        self.assertEqual(20, float(elem.get(u'x2')))
        self.assertEqual(30, float(elem.get(u'y2')))

        from ticketing.tickets.utils import parse_poly_data
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><polyline points="1,2 3,4 5,6" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        points = list(parse_poly_data(elem.get(u'points')))
        self.assertEqual(3, len(points))
        self.assertEqual((13., 23.), points[0])
        self.assertEqual((17., 27.), points[1])
        self.assertEqual((21., 31.), points[2])

    def testTransformApplierNested(self):
        from ticketing.tickets.cleaner import TransformApplier
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><g transform="translate(10, 20)"><g transform="matrix(1, 1, 1, 1, 0, 0)"><rect x="0" y="0" width="10" height="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></g></g></svg>''')
        TransformApplier()(svg)
        elem = svg[0][0][0]
        self.assertEqual(40, float(elem.get(u'x')))
        self.assertEqual(50, float(elem.get(u'y')))
        self.assertEqual(40, float(elem.get(u'width')))
        self.assertEqual(40, float(elem.get(u'height')))

