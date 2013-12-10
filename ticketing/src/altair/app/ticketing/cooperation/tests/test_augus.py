#-*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock
from StringIO import StringIO

from altair.app.ticketing.core.models import (
    Seat,
    AugusVenue,
    AugusSeat,
    CooperationTypeEnum,
    )

from altair.app.ticketing.cooperation.augus import (
    _sjis,
    SeatAugusSeatPairs,
    AugusTable,
    ImporterFactory,
    AugusVenueImporter,
    CSVEditorFactory,
    AugusCSVEditor,
    )

class SamplePairsFactory(object):
    def create(self):
        venue_id = 1
        seats = [Seat() for ii in range(0xff)]
        augus_venue = AugusVenue()
        augus_venue.save = Mock(return_value=None) # castration
        augus_venue.id = 1
        augus_venue.code = 555
        augus_seats = []
        for ii, seat in enumerate(seats):
            seat.save = Mock(return_value=None) # castration
            seat.id = ii
            seat.name = u'座席 {0}'.format(ii)
            seat.seat_no = u'{0}'.format(ii)
            seat.l0_id = u'l0-{0}'.format(ii)
            seat.row_l0_id = u'row-l0-{0}'.format(ii)
            seat.group_l0_id = u'group-l0-{0}'.format(ii)
            if ii % 2:
                augus_seat = AugusSeat()
                augus_seat.id = ii
                augus_seat.save = Mock(return_value=None) # castration
                augus_seat.seat_id = seat.id
                augus_seat.area_code = 999
                augus_seat.info_code = 888
                augus_seat.floor = '1'
                augus_seat.column = u'あ'
                augus_seat.num = u'{0}'.format(ii)
                augus_seat.augus_venue = augus_venue
                augus_seats.append(augus_seat)

        for ii in range(len(seats), len(seats)+30):
            augus_seat = AugusSeat()
            augus_seat.id = ii
            augus_seat.save = Mock(return_value=None)
            augus_seat.seat_id = None
            augus_seat.area_code = 999
            augus_seat.info_code = 888
            augus_seat.floor = '1'
            augus_seat.column = u'あ'
            augus_seat.num = u'{0}'.format(ii)
            augus_seats.append(augus_seat)

        pairs = SeatAugusSeatPairs(venue_id)
        pairs.load = Mock(return_value=None)
        pairs._seats = seats
        pairs._augus_seats = augus_seats
        return pairs

class AugusCSVImportTest(TestCase):
    def _test_get_original_venue(self):
        from altair.app.ticketing.cooperation.views import get_original_venue
        original_venue_id = 869
        target_venue_id = 6671
        organization_id = 15
        venue = get_original_venue(target_venue_id, organization_id)
        self.assertEqual(venue.id, original_venue_id)
        self.assertEqual(venue.organization_id, organization_id)
        self.assertEqual(venue.performance, None)

    def _test_csv_import(self):
        """
        from altair.app.ticketing.cooperation.views import update_augus_cooperation
        fp = StringIO()
        fp.write(CSVDATA)
        fp.seek(0)
        venue_id = 6671
        organization_id = 15
        update_augus_cooperation(venue_id, organization_id, fp)
        """

class SeatAugusSeatPairsTest(TestCase):
    def test_venue_id(self):
        venue_id = 1
        pairs = SeatAugusSeatPairs(venue_id)
        self.assertEqual(pairs.venue_id, venue_id)

class EncodeTest(TestCase):
    def test_sjis_encode(self):
        word = u'あるたいる'
        self.assertEqual(_sjis(word), word.encode('sjis'))

        with self.assertRaises(UnicodeDecodeError):
            _sjis(u'あるたいる'.encode('sjis'))

        with self.assertRaises(UnicodeDecodeError):
            _sjis('あるたいる')

        with self.assertRaises(ValueError):
            _sjis(None)


class AugusTableTest(TestCase):
    header_templates = ('id',
                        'name',
                        'seat_no',
                        'l0_id',
                        'group_l0_id',
                        'row_l0_id',
                        'augus_venue_code',
                        'augus_seat_area_code',
                        'augus_seat_info_code',
                        'augus_seat_floor',
                        'augus_seat_column',
                        'augus_seat_num'
                        )

    def test_get_header(self):
        table = AugusTable()
        header = table.get_header()
        for header_elm, header_tmpl in zip(header, self.header_templates):
            self.assertEqual(header_elm, header_tmpl,
                             'invalid header: {0} (tempaltes={1})'\
                             .format(header_elm, header_tmpl))
        self.assertEqual(len(header), len(self.header_templates),
                         'The number of header did not match.')

    def test_get_entry(self):
        factory = SamplePairsFactory()
        pairs = factory.create()
        table = AugusTable()
        for seat, augus_seat in pairs:
            entry = table.get_entry(seat, augus_seat)
            self.assertEqual(entry[0], seat.id)
            self.assertEqual(entry[1], _sjis(seat.name))
            self.assertEqual(entry[2], _sjis(seat.seat_no))
            self.assertEqual(entry[3], _sjis(seat.l0_id))
            self.assertEqual(entry[4], _sjis(seat.group_l0_id))
            self.assertEqual(entry[5], _sjis(seat.row_l0_id))
            if augus_seat:
                self.assertEqual(entry[6], augus_seat.augus_venue.code)
                self.assertEqual(entry[7], augus_seat.area_code)
                self.assertEqual(entry[8], augus_seat.info_code)
                self.assertEqual(entry[9], _sjis(augus_seat.floor))
                self.assertEqual(entry[10], _sjis(augus_seat.column))
                self.assertEqual(entry[11], _sjis(augus_seat.num))
            else:
                self.assertEqual(entry[6], '')
                self.assertEqual(entry[7], '')
                self.assertEqual(entry[8], '')
                self.assertEqual(entry[9], '')
                self.assertEqual(entry[10], '')
                self.assertEqual(entry[11], '')


class AugusVenueImporterTest(TestCase):
    def test_import_(self):
        factory = SamplePairsFactory()
        pairs = factory.create()
        io = StringIO()

class _FactoryTestBase(object):
    factory_class = None # need override
    type_class = () # need override

    def _test_create(self):
        for typ, class_ in self.type_class:
            ins = self.factory_class.create(typ)
            self.assertIsInstance(ins, class_)

class CSVEditorFactoryTest(TestCase, _FactoryTestBase):
    factory_class = CSVEditorFactory
    type_class = ((CooperationTypeEnum.augus.v[0], AugusCSVEditor),
                  )

    def test_create(self):
        self._test_create()

class ImporterFactoryTest(TestCase, _FactoryTestBase):
    factory_class = ImporterFactory
    type_class = ((CooperationTypeEnum.augus.v[0], AugusVenueImporter),
                  )

    def test_create(self):
        self._test_create()
