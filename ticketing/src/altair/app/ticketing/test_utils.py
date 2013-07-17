import unittest

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

    def test_todate(self):
        from .utils import todate
        from datetime import datetime, date
        for y in range(1900, 2100):
            for m in range(0, 12):
                for d in range(0, 30 if m != 1 else (28 + ((y % 4 == 0) - (y % 100 == 0) + (y % 400 == 0)))):
                    self.assertEquals(
                        date(y, m + 1, d + 1),
                        todate(datetime(y, m + 1, d + 1, 23, 59, 59)))
