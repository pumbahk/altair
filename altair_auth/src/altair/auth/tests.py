import os
import unittest
from pyramid import testing

here = os.path.dirname(__file__)

class TestIt(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def assertHasAttr(self, obj, attr_name):
        assert hasattr(obj, attr_name), u"{0} does'nt have {1}".format(obj, attr_name)

    def test_it(self):
        self.config.registry.settings['altair.auth.specs'] = [
            ('who1', 'altair.auth:test_conf/who1.ini')
            ]
        self.config.include('altair.auth')
        self.assertHasAttr(self.config, 'add_who_api_factory')
        from altair.auth import who_api
        request = testing.DummyRequest(environ={'wsgi.version': '1.0'})
        api = who_api(request, 'who1')
        self.assertIsNotNone(api)
