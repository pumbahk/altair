#-*- coding: utf-8 -*-
from unittest import TestCase
from StringIO import StringIO

from altair.app.ticketing.cooperation.augus import (
    _sjis,
    SeatAugusSeatPairs,
    AugusTable,
    )

CSVDATA = """2500003,20130927164400,1917,,,,,,,,,,,,,,,,
3,梅田芸術劇場メインホール,,,,0,1,1,23,1,6,40,6,40,0,0,0,1,1028952
3,梅田芸術劇場メインホール,,,,0,1,1,24,1,6,41,6,41,0,0,0,1,1028953
3,梅田芸術劇場メインホール,,,,0,1,1,25,1,6,42,6,42,0,0,0,1,1028954
3,梅田芸術劇場メインホール,,,,0,1,1,26,1,6,44,6,44,0,0,0,1,1028955
3,梅田芸術劇場メインホール,,,,0,1,1,27,1,6,45,6,45,0,0,0,1,1028956
3,梅田芸術劇場メインホール,,,,0,1,1,28,1,6,46,6,46,0,0,0,1,1028957
3,梅田芸術劇場メインホール,,,,0,1,1,29,1,6,47,6,47,0,0,0,1,1028958
"""

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
        
        with self.assertRaises(UnicodeEncodeError):
            _sjis('あるたいる'.encode('sjis'))
            
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
        header = table.get_heaer()
        for header_elm, header_tmpl in zip(header, self.header_templates):
            self.assertEqual(header_elm, header_tmpl,
                             'invalid header: {0} (tempaltes={1})'\
                             .format(header_elm, header_tmpl))
        self.assertEqual(len(header), len(self.header_templates),
                         'The number of header did not match.')
