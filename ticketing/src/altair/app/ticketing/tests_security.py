import unittest

import mock
from pyramid import testing

class auth_model_callbackTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.fc_auth_plugin = self._get_fc_auth_plugin()()
        self.rakuten_auth_plugin = self._get_rakuten_auth_plugin()(
            plugin_name='rakuten',
            endpoint='http://example.com/',
            verify_url='...',
            extra_verify_url='...',
            error_to='...',
            consumer_key='secret',
            session_factory=mock.Mock()
            )
        self.plugin_registry = mock.Mock()
        from altair.auth.interfaces import IPluginRegistry
        self.config.registry.registerUtility(self.plugin_registry, IPluginRegistry)

    def tearDown(self):
        testing.tearDown()

    def _get_fc_auth_plugin(self):
        from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin
        return FCAuthPlugin

    def _get_rakuten_auth_plugin(self):
        from altair.rakuten_auth.openid import RakutenOpenID
        return RakutenOpenID

    def _callFUT(self, *args, **kwargs):
        from .security import auth_model_callback
        return auth_model_callback(*args, **kwargs)

    def test_non_dict(self):
        identities = {}
        request = testing.DummyRequest()

        result = self._callFUT(identities, request)

        self.assertEqual(result, [])

    def test_membership(self):
        identities = { 'fc_auth': {'is_guest': True, 'membership': 'test-membership'}}
        request = testing.DummyRequest()

        self.plugin_registry.lookupp.return_value = self.fc_auth_plugin
        result = self._callFUT(identities, request)

        self.assertEqual(result, ['membership:test-membership', 'membership_source:fc_auth', 'altair_guest'])

    def test_membergroup(self):
        identities = { 'fc_auth': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup'} }
        request = testing.DummyRequest()

        self.plugin_registry.lookup.return_value = self.fc_auth_plugin
        result = self._callFUT(identities, request)

        self.assertEqual(result, ['auth_identifier:test', 'membership:test-membership', 'membership_source:fc_auth', 'membergroup:test-membergroup'])
        
    def test_claimed_id(self):
        identity = { 'rakuten': {'claimed_id': 'http://example.com'} }
        request = testing.DummyRequest()

        self.plugin_registry.lookup.return_value = self.rakuten_auth_plugin
        result = self._callFUT(identity, request)

        self.assertEqual(result, ['auth_identifier:http://example.com', 'membership:rakuten', 'membership_source:rakuten'])
