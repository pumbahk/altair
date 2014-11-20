# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock

class AltairGettiiVenueCSVRecordTest(TestCase):
    def _makeOne(self):
        from ..csvfile import AltairGettiiVenueCSVRecord
        return AltairGettiiVenueCSVRecord()

    def test_load(self):
        record = self._makeOne()
        seat = Mock()
        seat.id = 1
        seat.name = 'TEST'
        seat.seat_no = 'AA'
        seat.l0_id = 'ABC'
        seat.group_l0_id = 'DEF'
        seat.row_l0_id = 'GHI'

        gettii_seat = Mock()
        gettii_seat.gettii_venue = Mock()
        gettii_seat.gettii_venue.code = 'aaa'
        gettii_seat.l0_id = 'a'
        gettii_seat.coordx = 'b'
        gettii_seat.coordy = 'c'
        gettii_seat.posx = 'd'
        gettii_seat.posy = 'e'
        gettii_seat.angle = 'f'
        gettii_seat.floor = 'g'
        gettii_seat.column = 'h'
        gettii_seat.num = 'i'
        gettii_seat.block = 'j'
        gettii_seat.gate = 'k'
        gettii_seat.priority_block = 'l'
        gettii_seat.priority_seat = 'm'
        gettii_seat.seat_flag = 'n'
        gettii_seat.seat_classif = 'o'
        gettii_seat.net_block = 'p'
        gettii_seat.modified_at = 'q'

        target = self._makeOne()
        target.load(seat, gettii_seat)

        self.assertEqual(target.id_, seat.id)
        self.assertEqual(target.name, seat.name)
        self.assertEqual(target.seat_no, seat.seat_no)
        self.assertEqual(target.l0_id, seat.l0_id)
        self.assertEqual(target.group_l0_id, seat.group_l0_id)
        self.assertEqual(target.row_l0_id, seat.row_l0_id)
        self.assertEqual(target.gettii_venue_code, gettii_seat.gettii_venue.code)
        self.assertEqual(target.gettii_l0_id, gettii_seat.l0_id)
        self.assertEqual(target.gettii_coodx, gettii_seat.coordx)
        self.assertEqual(target.gettii_coody, gettii_seat.coordy)
        self.assertEqual(target.gettii_posx, gettii_seat.posx)
        self.assertEqual(target.gettii_posy, gettii_seat.posy)
        self.assertEqual(target.gettii_angle, gettii_seat.angle)
        self.assertEqual(target.gettii_floor, gettii_seat.floor)
        self.assertEqual(target.gettii_column, gettii_seat.column)
        self.assertEqual(target.gettii_num, gettii_seat.num)
        self.assertEqual(target.gettii_block, gettii_seat.block)
        self.assertEqual(target.gettii_gate, gettii_seat.gate)
        self.assertEqual(target.gettii_priority, '')
        self.assertEqual(target.gettii_area_code, '')
        self.assertEqual(target.gettii_priority_block, gettii_seat.priority_block)
        self.assertEqual(target.gettii_priority_seat, gettii_seat.priority_seat)
        self.assertEqual(target.gettii_seat_flag, gettii_seat.seat_flag)
        self.assertEqual(target.gettii_seat_classif, gettii_seat.seat_classif)
        self.assertEqual(target.gettii_net_block, gettii_seat.net_block)
        self.assertEqual(target.gettii_modifier, '')
        self.assertEqual(target.gettii_modified_at, gettii_seat.modified_at)


class AltairGettiiVenueCSVTest(TestCase):
    def _makeOne(self):
        from ..csvfile import AltairGettiiVenueCSV
        return AltairGettiiVenueCSV()

    def test_load(self):
        venue = Mock()
        venue.id = 1
        venue.seats = [Mock() for ii in range(10)]
        gettii_csv = self._makeOne()
        gettii_csv.load(venue)


class GettiiSeatCSV(TestCase):
    def _makeOne(self):
        from ..csvfile import GettiiSeatCSV
        return GettiiSeatCSV()

    def test_load(self):
        venue = Mock()
        venue.id = 1
        venue.seats = [Mock() for ii in range(10)]
        gettii_csv = self._makeOne()
        gettii_csv.load(venue)
