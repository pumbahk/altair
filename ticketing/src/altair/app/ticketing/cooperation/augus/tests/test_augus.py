#-*- coding: utf-8 -*-
from unittest import TestCase
from mock import Mock
import csv
from StringIO import StringIO
from altair.app.ticketing.core.models import (
    Seat,
    AugusVenue,
    AugusSeat,
    CooperationTypeEnum,
    )
from ..csveditor import (
    _sjis,
    AugusTable,
    ImporterFactory,
    AugusVenueImporter,
    CSVEditorFactory,
    AugusCSVEditor,
    )
from ..utils import (
    SeatAugusSeatPairs,
    )


class SamplePairsFactory(object):
    def create(self):
        venue_id = 1
        seats = [Seat() for ii in range(0xff)]
        augus_venue = AugusVenue()
        augus_venue.save = Mock(return_value=None) # castration
        augus_venue.id = 1
        augus_venue.code = 555
        augus_venue.version = 12
        augus_venue.name = u'おーがす用会場'
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
                augus_seat.area_name = u'エリア名'                
                augus_seat.info_name = u'付加情報名'                
                augus_seat.doorway_name = u'出入口名'                
                augus_seat.priority = 1
                augus_seat.floor = '1'
                augus_seat.column = u'あ'
                augus_seat.num = u'{0}'.format(ii)
                augus_seat.block = 2
                augus_seat.coordy = 3
                augus_seat.coordx = 4
                augus_seat.coordy_whole = 5
                augus_seat.coordx_whole = 6
                augus_seat.area_code = 7
                augus_seat.info_code = 8
                augus_seat.doorway_code = 9
                augus_seat.version = 12
                augus_seat.augus_venue = augus_venue
                augus_seats.append(augus_seat)

        for ii in range(len(seats), len(seats)+30):
            augus_seat = AugusSeat()
            augus_seat.id = ii
            augus_seat.save = Mock(return_value=None)
            augus_seat.seat_id = None
            augus_seat.area_name = u'エリア名'                
            augus_seat.info_name = u'付加情報名'                
            augus_seat.doorway_name = u'出入口名'                
            augus_seat.priority = 1
            augus_seat.floor = '1'
            augus_seat.column = u'あ'
            augus_seat.num = u'{0}'.format(ii)
            augus_seat.block = 2
            augus_seat.coordy = 3
            augus_seat.coordx = 4
            augus_seat.coordy_whole = 5
            augus_seat.coordx_whole = 6
            augus_seat.area_code = 999
            augus_seat.info_code = 888
            augus_seat.doorway_code = 9
            augus_seat.version = 10
            augus_seats.append(augus_seat)
            
        pairs = SeatAugusSeatPairs()
        pairs.get_seats = Mock(return_value=seats)
        pairs.get_augus_seats = Mock(return_value=augus_seats)
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
        venue = Mock()
        venue.id = 1
        pairs = SeatAugusSeatPairs()
        pairs.load(venue)
        self.assertEqual(pairs.venue_id, venue.id)

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
                        'augus_venue_name',
                        'augus_seat_area_name',
                        'augus_seat_info_name',
                        'augus_seat_doorway_name',
                        'augus_seat_priority',
                        'augus_seat_floor',
                        'augus_seat_column',
                        'augus_seat_num',
                        'augus_seat_block',
                        'augus_seat_coordy',
                        'augus_seat_coordx',
                        'augus_seat_coordy_whole',
                        'augus_seat_coordx_whole',
                        'augus_seat_area_code',
                        'augus_seat_info_code',
                        'augus_seat_doorway_code',
                        'augus_venue_version',
                        )

    def test_get_header(self):
        table = AugusTable()
        header = table.get_header()
        for header_elm, header_tmpl in zip(header, self.header_templates):
            self.assertEqual(header_elm, header_tmpl,
                             'invalid header: {0} (templates={1})'\
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
                self.assertEqual(entry[7], _sjis(augus_seat.augus_venue.name))
                self.assertEqual(entry[8], _sjis(augus_seat.area_name))
                self.assertEqual(entry[9], _sjis(augus_seat.info_name))
                self.assertEqual(entry[10], _sjis(augus_seat.doorway_name))                
                self.assertEqual(entry[11], augus_seat.priority)
                self.assertEqual(entry[12], _sjis(augus_seat.floor))
                self.assertEqual(entry[13], _sjis(augus_seat.column))
                self.assertEqual(entry[14], _sjis(augus_seat.num))
                self.assertEqual(entry[15], augus_seat.block)
                self.assertEqual(entry[16], augus_seat.coordy)
                self.assertEqual(entry[17], augus_seat.coordx)
                self.assertEqual(entry[18], augus_seat.coordy_whole)
                self.assertEqual(entry[19], augus_seat.coordx_whole)
                self.assertEqual(entry[20], augus_seat.area_code)
                self.assertEqual(entry[21], augus_seat.info_code)
                self.assertEqual(entry[22], augus_seat.doorway_code)
                self.assertEqual(entry[23], augus_seat.version)
                
            else:
                for ii in range(6, 24):
                    self.assertEqual(entry[ii], '')

class AugusVenueImporterTest(TestCase):
    def test_import_(self):
        factory = SamplePairsFactory()
        pairs = factory.create()
        io = StringIO()        

        # create csv
        writer = csv.writer(io)
        typ = CooperationTypeEnum.augus.v[0]
        editor = CSVEditorFactory.create(typ)
        editor.write(writer, pairs)
        
        # test improter
        io.seek(0)
        reader = csv.reader(io)
        


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
