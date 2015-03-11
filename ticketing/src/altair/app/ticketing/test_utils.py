import unittest
from datetime import datetime, timedelta
from altair.app.ticketing.utils import DateTimeRange

class UtilsTest(unittest.TestCase):
    def test_todatetime(self):
        from .utils import todatetime
        from datetime import datetime, date
        for y in range(1900, 2100):
            for m in range(0, 12):
                for d in range(0, 30 if m != 1 else (28 + ((y % 4 == 0) - (y % 100 == 0) + (y % 400 == 0)))):
                    self.assertEquals(
                        datetime(y, m + 1, d + 1, 0, 0, 0),
                        todatetime(date(y, m + 1, d + 1)))

    def test_todatetime_from_datetime(self):
        from .utils import todatetime
        from datetime import datetime, date
        now = datetime.now()
        self.assertEquals(now, todatetime(now))

    def test_todate(self):
        from .utils import todate
        from datetime import datetime, date
        for y in range(1900, 2100):
            for m in range(0, 12):
                for d in range(0, 30 if m != 1 else (28 + ((y % 4 == 0) - (y % 100 == 0) + (y % 400 == 0)))):
                    self.assertEquals(
                        date(y, m + 1, d + 1),
                        todate(datetime(y, m + 1, d + 1, 23, 59, 59)))

class DateTimeRangeTest(unittest.TestCase):
    # Case 1) Cross overlap
    def test_cross_overlap(self):
        start1 = datetime.now()
        end1 = datetime.now() + timedelta(days=10)
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=5)
        end2 = datetime.now() + timedelta(days=10)
        dt_range2 = DateTimeRange(start2, end2)

        # (now, now + 10 days) and (now - 5 days, now + 10 days) overlaps
        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlaps")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlaps")

    # Case 2) Complete overlap
    def test_complete_overlap(self):
        start1 = datetime.now()
        end1 = datetime.now() + timedelta(days=2)
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=2)
        end2 = datetime.now() + timedelta(days=5)
        dt_range2 = DateTimeRange(start2, end2)

        # (now, now + 2 days) and (now - 2 days, now + 5 days) overlaps
        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlaps")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlaps")

    # Case 3) No overlap
    def test_no_overlap(self):
        # Case 3) (now, now + 2 days) and (now + 3 days, now + 8 days) doesn't overlap
        start1 = datetime.now()
        end1 = datetime.now() + timedelta(days=2)
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() + timedelta(days=3)
        end2 = datetime.now() + timedelta(days=8)
        dt_range2 = DateTimeRange(start2, end2)

        self.assertFalse(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " doesn't overlap")
        self.assertFalse(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " doesn't overlap")

    # Case 4) Cross overlap with left None
    def test_cross_overlap_with_left_none(self):
        start1 = None
        end1 = datetime.now()
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=3)
        end2 = datetime.now() + timedelta(days=2)
        dt_range2 = DateTimeRange(start2, end2)

        # (None, now) and (now - 3 days, now + 2 days) overlaps
        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlaps")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlaps")

    # Case 5) Cross overlap with right None
    def test_cross_overlap_with_right_none(self):
        start1 = datetime.now()
        end1 = None
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=2)
        end2 = datetime.now() + timedelta(days=3)
        dt_range2 = DateTimeRange(start2, end2)

        # (now, None) and (now - 3 days, now + 4 days) overlaps
        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlaps")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlaps")

    # Case 6) No overlap with left none
    def test_no_overlap_with_left_none(self):
        start1 = None
        end1 = datetime.now()
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() + timedelta(days=1)
        end2 = datetime.now() + timedelta(days=3)
        dt_range2 = DateTimeRange(start2, end2)

        # (None, now) and (now + 1 day, now + 3 days) doesn't overlap
        self.assertFalse(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " doesn't overlap")
        self.assertFalse(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " doesn't overlap")


    # Case 7) No overlap with right none
    def test_no_overlap_with_right_none(self):
        start1 = datetime.now()
        end1 = None
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=5)
        end2 = datetime.now() - timedelta(days=2)
        dt_range2 = DateTimeRange(start2, end2)

        # (now, None) and (now - 5 day, now - 2 days) doesn't overlap
        self.assertFalse(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " doesn't overlap")
        self.assertFalse(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " doesn't overlap")


    # Case 8) Overlap with both none
    def test_overlap_both_none(self):
        start1 = None
        end1 = None
        dt_range1 = DateTimeRange(start1, end1)
        start2 = datetime.now() - timedelta(days=2)
        end2 = datetime.now() + timedelta(days=5)
        dt_range2 = DateTimeRange(start2, end2)

        # (none, None) and (now - 2 days, now + 5 days) overlaps
        self.assertTrue(dt_range1.overlap(dt_range2), str(dt_range1) + " and " + str(dt_range2) + " overlap")
        self.assertTrue(dt_range2.overlap(dt_range1), str(dt_range2) + " and " + str(dt_range1) + " overlap")