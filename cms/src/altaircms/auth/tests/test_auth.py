# coding: utf-8
import unittest
from httplib2 import Response
import mock
from pyramid import testing
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPUnauthorized

from altaircms.lib.testutils import BaseTest, _initTestingDB
from altaircms.auth.initial_data import insert_initial_authdata

def setup_module():
    _initTestingDB()
    import sqlahelper
    sqlahelper.get_engine().echo = False

def teardown_module():
    import transaction
    transaction.abort()

class OAuthLoginTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'altair.oauth.client_id': 'fa12a58972626f0597c2faee1454e1',
            'altair.oauth.secret_key': 'c5f20843c65870fad8550e3ad1f868',
            'altair.oauth.authorize_url': 'http://localhost:7654/api/authorize',
            'altair.oauth.access_token_url': 'http://localhost:7654/api/access_token'
            })

        insert_initial_authdata()

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _getTarget(self):
        from ..views import OAuthLogin
        return OAuthLogin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_oauth_entry(self):
        request = testing.DummyRequest()
        target = self._makeOne(request, authorize_url="http://localhost:7654/login/authorize")

        result = target.oauth_entry()
        
        self.assertEqual(result.location, 
                         'http://localhost:7654/login/authorize?client_id=fa12a58972626f0597c2faee1454e1&response_type=code')


    @mock.patch("urllib2.urlopen")
    def test_oauth_callback_ioerror(self, mock_urlopen):
        mock_urlopen.side_effect = IOError

        request = testing.DummyRequest(GET={
                "code": "",
                })

        target = self._makeOne(request)

        result = target.oauth_callback()

    @mock.patch("urllib2.urlopen")
    def test_oauth_callback_with_register(self, mock_urlopen):
        from StringIO import StringIO
        import json

        self.config.add_route('dashboard', '/')

        mock_urlopen.return_value = StringIO(json.dumps({
                    "user_id": "dummy-user-id",
                    "screen_name": "dummy_screen_name",
                    "access_token": "access_token",
                    
                    }))

        request = testing.DummyRequest(GET={
                "code": "",
                }, registry=self.config)

        target = self._makeOne(request)

        result = target.oauth_callback()

        self.assertEqual(result.location, "http://example.com/")


class TestSecurity(BaseTest):

    def tearDown(self):
        from altaircms.lib.testutils import dropall_db
        dropall_db()
        from altaircms.lib.testutils import create_db
        create_db()
        import transaction
        transaction.abort()

    def test_user_notfound(self):
        from altaircms.security import rolefinder
        request = testing.DummyRequest()
        self.assertEqual(rolefinder(1234, request), [])

