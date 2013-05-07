from unittest import TestCase
from pyramid import testing
from . import CONFIG_PREFIX, includeme

class TestApi(TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)
        includeme(self.config)

    def tearDown(self):
        testing.tearDown()

    def test_get_timezone_1(self):
        from api import get_timezone
        self.config.registry.settings[CONFIG_PREFIX + 'timezone'] = 'UTC'
        self.assertEqual(get_timezone(self.request).zone, 'UTC')

    def test_get_timezone_2(self):
        from datetime import datetime, timedelta
        from api import get_timezone
        import os
        import time
        os.environ['TZ'] = 'Asia/Tokyo'
        time.tzset() 
        self.assertEqual(get_timezone(self.request).utcoffset(datetime(2013, 1, 1, 0, 0, 0)), timedelta(0, 32400))

    def test_get_timezone_3(self):
        from api import get_timezone
        self.assertEqual(get_timezone(self.request, 'Asia/Tokyo').zone, 'Asia/Tokyo')


