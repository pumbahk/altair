# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock


class GettiiImporterFuncTest(TestCase):
    def _makeOne(self):
        from ..importers import get_or_create_gettii_seat
        return get_or_create_gettii_seat

    def test_get_or_create_gettii_seat(self):
        external_venue = Mock()
        external_venue.id = 1
        external_l0_id = '111'
        func = self._makeOne()
        func(external_venue, external_l0_id)


class GettiiVenueImpoterTest(TestCase):
    def _makeOne(self):
        from ..importers import GettiiVenueImpoter
        return GettiiVenueImpoter()

    def test_import_record(self):
        from ..importers import GettiiVenueImportError
        venue_id = 1
        record = Mock()
        record.id_ = 2
        record.gettii_venue_code = 3

        target = self._makeOne()
        with self.assertRaises(GettiiVenueImportError):
            target._import_record(venue_id, record)

    def test_is_match(self):
        record = Mock()
        gettii_seat = Mock()
        target = self._makeOne()
        target.is_match(record, gettii_seat)

    def test_update_gettii_seat_from_record(self):
        record = Mock()
        gettii_seat = Mock()
        target = self._makeOne()
        target.update_gettii_seat_from_record(record, gettii_seat)
