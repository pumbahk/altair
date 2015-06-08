import unittest

class DurationParserTest(unittest.TestCase):
    def test_it(self):
        from .duration import parse_duration
        from datetime import timedelta
        self.assertEqual(parse_duration(u'12:00', '%H:%M'), timedelta(seconds=43200))
        self.assertEqual(parse_duration(u'24:00', '%H:%M'), timedelta(days=1))
        self.assertEqual(parse_duration(u'2400', '%H%M'), timedelta(days=1))
        self.assertEqual(parse_duration(u'10000', '%H%M'), timedelta(days=4, seconds=14400))

class DurationBuilderTest(unittest.TestCase):
    def test_it(self):
        from .duration import build_duration 
        from datetime import timedelta
        self.assertEqual(build_duration(timedelta(seconds=43200), '%H:%M'), u'12:00')
        self.assertEqual(build_duration(timedelta(days=1), '%H:%M'), u'24:00')
        self.assertEqual(build_duration(timedelta(days=1), '%H%M'), u'2400')
        self.assertEqual(build_duration(timedelta(days=4, seconds=14400), '%H%M'), u'10000')


