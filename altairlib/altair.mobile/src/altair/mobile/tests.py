from unittest import TestCase
from pyramid import testing 

class RegressionTest(TestCase):
    def setUp(self):
        config = testing.setUp()
        config.include('.'.join(__name__.split('.')[0:-1]))
        self.config = config

    def tearDown(self):
        testing.tearDown()

    def test_detect_from_email_address(self):
        from .api import detect_from_email_address
        from .carriers import NonMobile, DoCoMo
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@example.com'),
            NonMobile)
        self.assertEqual(
            detect_from_email_address(self.config.registry, 'test@docomo.ne.jp'),
            DoCoMo)


