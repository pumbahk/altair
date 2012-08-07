# -*- coding: utf-8 -*-
import os
from unittest import TestCase

from ...core.models import Seat, SeatStatusEnum
from . import sheet


class DummySeat(dict):
    pass


class SeatSourceFromSeatTest(TestCase):
    """SeatからSeatSourceへの変換テスト"""
    def setUp(self):
        self.seat = DummySeat()
        self.seat["block"] = u"テストブロック"
        self.seat["floor"] = u"1階"
        self.seat["row"] = u"あ"
        self.seat["seat"] = u"A1"
        self.seat.status = SeatStatusEnum.Vacant

    def test_ok(self):
        result = sheet.seat_source_from_seat(self.seat)
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
            seat=u"A1",
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A2",
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"B1",
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"C15",
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"い",
            seat=u"A1",
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"2階",
            line=u"あ",
            seat=u"A1",
        ))

    def test_ok(self):
        result = sheet.seat_records_from_seat_sources(self.seat_sources)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].line, u"あ")
        self.assertEqual(result[0].start, "A1")
        self.assertEqual(result[0].end, "C15")
        self.assertEqual(result[0].quantity, 4)
        self.assertEqual(result[1].line, u"い")
        self.assertEqual(result[1].start, "A1")
        self.assertEqual(result[1].end, "A1")
        self.assertEqual(result[1].quantity, 1)
        self.assertEqual(result[2].line, u"あ")
        self.assertEqual(result[2].start, "A1")
        self.assertEqual(result[2].end, "A1")
        self.assertEqual(result[2].quantity, 1)


class SeatRecordsFromSeatSourcesUnsold(TestCase):
    def setUp(self):
        self.seat_sources = []
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A1",
            status=SeatStatusEnum.Vacant.v,
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A2",
            status=SeatStatusEnum.Vacant.v,
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A3",
            status=SeatStatusEnum.Vacant.v,
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A4",
            status=SeatStatusEnum.NotOnSale.v,
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A5",
            status=SeatStatusEnum.Vacant.v,
        ))
        self.seat_sources.append(sheet.SeatSource(
            block=u"テストブロック",
            floor=u"1階",
            line=u"あ",
            seat=u"A6",
            status=SeatStatusEnum.Vacant.v,
        ))

    def test_ok(self):
        result = sheet.seat_records_from_seat_sources_unsold(self.seat_sources)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].line, u"あ")
        self.assertEqual(result[0].start, "A1")
        self.assertEqual(result[0].end, "A3")
        self.assertEqual(result[0].quantity, 3)
        self.assertEqual(result[1].line, u"あ")
        self.assertEqual(result[1].start, "A5")
        self.assertEqual(result[1].end, "A6")
        self.assertEqual(result[1].quantity, 2)
