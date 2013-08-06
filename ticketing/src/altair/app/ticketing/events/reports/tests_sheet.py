# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from datetime import datetime, date
from ...core.models import Seat, SeatStatusEnum
from . import sheet


class DummyObject(object):
    def __setitem__(self, k, v):
        self.attributes[k] = v

    def __getitem__(self, k):
        return self.attributes[k]

    def __init__(self, **kwargs):
        self.attributes = {}
        for k, v in kwargs.items():
            setattr(self, k, v)

class DummySeat(DummyObject):
    pass

class DummyVenueArea(DummyObject):
    pass

class SeatSourceFromSeatTest(TestCase):
    """SeatからSeatSourceへの変換テスト"""
    def setUp(self):
        self.seat = DummySeat(
            attributes=dict(
                block=u"テストブロック",
                floor=u"1階",
                row=u"あ",
                seat=u"A1"
                ),
            status=SeatStatusEnum.Vacant,
            venue_id=1,
            row_l0_id='r',
            group_l0_id='g',
            seat_no='A1',
            areas=[DummyVenueArea(name=u'テストブロック')]
            )

    def test_ok(self):
        result = sheet.seat_source_from_seat(self.seat)
        self.assertEqual(result.source, self.seat)
        self.assertEqual(result.block, self.seat["block"])
        self.assertEqual(result.floor, self.seat["floor"])
        self.assertEqual(result.line, self.seat["row"])
        self.assertEqual(result.seat, self.seat["seat"])


class SeatRecordsFromSeatSources(TestCase):
    def setUp(self):
        self.seat_sources = []
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"1",
            source=DummySeat(row_l0_id=u'r', areas=[DummyVenueArea()])
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"2",
            source=DummySeat(row_l0_id=u'r', areas=[DummyVenueArea()])
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"3",
            source=DummySeat(row_l0_id=u'r', areas=[DummyVenueArea()])
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"4",
            source=DummySeat(row_l0_id=u'r', areas=[DummyVenueArea()])
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"い",
            seat=u"1",
            source=DummySeat(row_l0_id=u's', areas=[DummyVenueArea()])
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"2階",
            line=u"あ",
            seat=u"1",
            source=DummySeat(row_l0_id=u'r', areas=[DummyVenueArea()])
        ))

    def test_ok(self):
        result = sheet.seat_records_from_seat_sources(self.seat_sources, report_type='sold', kind='stocks', date=datetime.now())
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].line, u"あ")
        self.assertEqual(result[0].start, "1")
        self.assertEqual(result[0].end, "4")
        self.assertEqual(result[0].quantity, 4)
        self.assertEqual(result[1].line, u"い")
        self.assertEqual(result[1].start, "1")
        self.assertEqual(result[1].end, "1")
        self.assertEqual(result[1].quantity, 1)
        self.assertEqual(result[2].line, u"あ")
        self.assertEqual(result[2].start, "1")
        self.assertEqual(result[2].end, "1")
        self.assertEqual(result[2].quantity, 1)


class SeatRecordsFromSeatSourcesUnsold(TestCase):
    def setUp(self):
        self.seat_sources = []
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"1",
            status=SeatStatusEnum.Vacant.v,
            source=DummySeat(row_l0_id=u'r')
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"2",
            status=SeatStatusEnum.Vacant.v,
            source=DummySeat(row_l0_id=u'r')
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"3",
            status=SeatStatusEnum.Vacant.v,
            source=DummySeat(row_l0_id=u'r')
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"4",
            status=SeatStatusEnum.NotOnSale.v,
            source=DummySeat(row_l0_id=u'r')
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"5",
            status=SeatStatusEnum.Vacant.v,
            source=DummySeat(row_l0_id=u'r')
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"6",
            status=SeatStatusEnum.Vacant.v,
            source=DummySeat(row_l0_id=u'r')
        ))

    def test_ok(self):
        result = sheet.seat_records_from_seat_sources(self.seat_sources, report_type='unsold', kind='stocks', date=datetime.now())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].line, u"あ")
        self.assertEqual(result[0].start, "1")
        self.assertEqual(result[0].end, "3")
        self.assertEqual(result[0].quantity, 3)
        self.assertEqual(result[1].line, u"あ")
        self.assertEqual(result[1].start, "5")
        self.assertEqual(result[1].end, "6")
        self.assertEqual(result[1].quantity, 2)
