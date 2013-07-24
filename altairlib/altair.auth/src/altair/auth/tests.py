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
        from altair.auth import (
            who_api,
            who_api_factory,
            decide,
            list_who_api_factory,
        )

        self.config.registry.settings.update(
            {'altair.auth.specs': [
                    ('who1', 'altair.auth:test_conf/who1.ini'),
                    ('who2', 'altair.auth:test_conf/who1.ini')
                    ],
             'altair.auth.decider': 'altair.auth.testing:DummyDecider'})
        self.config.testing_securitypolicy()
        self.config.include('altair.auth')
        self.assertHasAttr(self.config, 'add_who_api_factory')
        request = testing.DummyRequest(environ={'wsgi.version': '1.0'})
        api = who_api(request, 'who1')
        self.assertIsNotNone(api)
        request.testing_who_api_name = 'testing_who'
        api_name = decide(request)
        self.assertEqual(api_name, 'testing_who')

        factories = list_who_api_factory(request)

        self.assertEqual(factories, 
                         [(u'who1', who_api_factory(request, 'who1')),
                          (u'who2', who_api_factory(request, 'who2'))])
