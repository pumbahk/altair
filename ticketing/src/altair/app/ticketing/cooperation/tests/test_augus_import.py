#-*- coding: utf-8 -*-
from unittest import TestCase
from StringIO import StringIO

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
    def test_get_original_venue(self):
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
