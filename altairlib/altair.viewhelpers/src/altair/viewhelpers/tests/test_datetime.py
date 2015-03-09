from unittest import TestCase
from datetime import datetime, timedelta
from altair.viewhelpers.datetime_ import DateTimeRange

class DateTimeRangeTest(TestCase):
    def test_overlap(self):
        # Case 1) (now, now + 10 days) and (now - 5 days, now + 10 days) overlaps
        start1 = datetime.now()
        end1 = datetime.now() + timedelta(days=10)
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=5)
        end2 = datetime.now() + timedelta(days=10)
        dt_range2 = DateTimeRange(start2, end2)

        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlaps")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlaps")


        # Case 2) (now, now + 2 days) and (now - 2 days, now + 5 days) overlaps
        start3 = datetime.now()
        end3 = datetime.now() + timedelta(days=2)
        dt_range3 = DateTimeRange(start3, end3)
        start4 = datetime.now() - timedelta(days=2)
        end4 = datetime.now() + timedelta(days=5)
        dt_range4 = DateTimeRange(start4, end4)

        self.assertTrue(dt_range3.overlap(dt_range4), str(dt_range3) + " and " + str(dt_range4) + " overlaps")
        self.assertTrue(dt_range4.overlap(dt_range3), str(dt_range4) + " and " + str(dt_range3) + " overlaps")


        # Case 3) (now, now + 2 days) and (now + 3 days, now + 8 days) doesn't overlap
        start5 = datetime.now()
        end5 = datetime.now() + timedelta(days=2)
        dt_range5 = DateTimeRange(start5, end5)
        start6 = datetime.now() + timedelta(days=3)
        end6 = datetime.now() + timedelta(days=8)
        dt_range6 = DateTimeRange(start6, end6)

        self.assertFalse(dt_range5.overlap(dt_range6), str(dt_range5) + " and " + str(dt_range6) + " doesn't overlap")
        self.assertFalse(dt_range6.overlap(dt_range5), str(dt_range6) + " and " + str(dt_range5) + " doesn't overlap")


        # Case 4) (None, now) and (now - 3 days, now + 2 days) overlaps
        start7 = None
        end7 = datetime.now()
        dt_range7 = DateTimeRange(start7, end7)
        start8 = datetime.now() - timedelta(days=3)
        end8 = datetime.now() + timedelta(days=2)
        dt_range8 = DateTimeRange(start8, end8)

        self.assertTrue(dt_range7.overlap(dt_range8), str(dt_range7) + " and " + str(dt_range8) + " overlaps")
        self.assertTrue(dt_range8.overlap(dt_range7), str(dt_range8) + " and " + str(dt_range7) + " overlaps")


        # Case 5) (now, None) and (now - 3 days, now + 4 days) overlaps
        start9 = datetime.now()
        end9 = None
        dt_range9 = DateTimeRange(start9, end9)
        start10 = datetime.now() - timedelta(days=2)
        end10 = datetime.now() + timedelta(days=3)
        dt_range10 = DateTimeRange(start10, end10)

        self.assertTrue(dt_range9.overlap(dt_range10), str(dt_range9) + " and " + str(dt_range10) + " overlaps")
        self.assertTrue(dt_range10.overlap(dt_range9), str(dt_range10) + " and " + str(dt_range9) + " overlaps")


        # Case 6) (None, now) and (now + 1 day, now + 3 days) doesn't overlap
        start11 = None
        end11 = datetime.now()
        dt_range11 = DateTimeRange(start11, end11)
        start12 = datetime.now() + timedelta(days=1)
        end12 = datetime.now() + timedelta(days=3)
        dt_range12 = DateTimeRange(start12, end12)

        self.assertFalse(dt_range11.overlap(dt_range12), str(dt_range11) + " and " + str(dt_range12) + " doesn't overlap")
        self.assertFalse(dt_range12.overlap(dt_range11), str(dt_range12) + " and " + str(dt_range11) + " doesn't overlap")


        # Case 7) (now, None) and (now - 5 day, now - 2 days) doesn't overlap
        start13 = datetime.now()
        end13 = None
        dt_range13 = DateTimeRange(start13, end13)
        start14 = datetime.now() - timedelta(days=5)
        end14 = datetime.now() - timedelta(days=2)
        dt_range14 = DateTimeRange(start14, end14)

        self.assertFalse(dt_range13.overlap(dt_range14), str(dt_range13) + " and " + str(dt_range14) + " doesn't overlap")
        self.assertFalse(dt_range14.overlap(dt_range13), str(dt_range14) + " and " + str(dt_range13) + " doesn't overlap")


        # Case 8) (none, None) and (now - 2 days, now + 5 days) overlaps
        start15 = None
        end15 = None
        dt_range15 = DateTimeRange(start15, end15)
        start16 = datetime.now() - timedelta(days=2)
        end16 = datetime.now() + timedelta(days=5)
        dt_range16 = DateTimeRange(start16, end16)

        self.assertTrue(dt_range15.overlap(dt_range16), str(dt_range15) + " and " + str(dt_range16) + " overlap")
        self.assertTrue(dt_range16.overlap(dt_range15), str(dt_range16) + " and " + str(dt_range15) + " overlap")