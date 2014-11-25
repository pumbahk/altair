# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock


class SeatAugusSeatPairsTest(TestCase):
    def _makeOne(self):
        from ..utils import SeatAugusSeatPairs
        pair = SeatAugusSeatPairs()
        return pair

    def test_iter(self):
        from ..errors import IllegalDataError
        target = self._makeOne()
        target._venue = Mock()
        target._augus_venue = Mock()
        target._venue.id = 1
        target._augus_venue.venue.id = 2
        iterator = iter(target)
        with self.assertRaises(IllegalDataError):
            iterator.next()
