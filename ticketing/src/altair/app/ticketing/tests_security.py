import unittest

import mock
from pyramid import testing

class AuthModelCallbackTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.fc_auth_plugin = self._get_fc_auth_plugin()()
        self.rakuten_auth_plugin = self._get_rakuten_auth_plugin()(
            plugin_name='rakuten',
            endpoint='http://example.com/',
            url_builder=mock.Mock(
                verify_url='...',
                extra_verify_url='...',
                error_to='...'
                ),
            consumer_key='secret',
            session_factory=mock.Mock()
            )
        self.nogizaka46_auth_plugin = self._get_nogizaka46_auth_plugin()
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

    def _get_nogizaka46_auth_plugin(self):
        from altair.app.ticketing.project_specific.nogizaka46.auth import NogizakaAuthPlugin
        return NogizakaAuthPlugin

    def _getTarget(self):
        from .security import AuthModelCallback
        return AuthModelCallback

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_non_dict(self):
        identities = {}
        request = testing.DummyRequest()
        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, [])

    def test_membership(self):
        identities = { 'fc_auth': {'is_guest': True, 'membership': 'test-membership'}}
        request = testing.DummyRequest()

        self.plugin_registry.lookup.return_value = self.fc_auth_plugin

        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['membership:test-membership', 'membership_source:fc_auth', 'altair_guest'])

    def test_membergroup(self):
        identities = { 'fc_auth': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup'} }
        request = testing.DummyRequest()

        self.plugin_registry.lookup.return_value = self.fc_auth_plugin

        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:test', 'authz_identifier:test', 'membership:test-membership', 'membership_source:fc_auth', 'membergroup:test-membergroup'])
        
    def test_claimed_id(self):
        identities = { 'rakuten': {'claimed_id': 'http://example.com'} }
        request = testing.DummyRequest()

        self.plugin_registry.lookup.return_value = self.rakuten_auth_plugin

        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:http://example.com', 'authz_identifier:http://example.com', 'membership:rakuten', 'membership_source:rakuten'])

    def test_priority_implicit(self):
        identities = {
            'fc_auth': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup' },
            'rakuten': {'claimed_id': 'http://example.com', 'membership': 'rakuten'},
            }
        request = testing.DummyRequest()

        dummy_plugin = mock.Mock()
        dummy_plugin.name = 'unknown'
        from altair.auth.interfaces import IAuthenticator
        from zope.interface import directlyProvides
        directlyProvides(dummy_plugin, IAuthenticator)

        self.plugin_registry.lookup = lambda v: {
            'fc_auth': self.fc_auth_plugin,
            'rakuten': self.rakuten_auth_plugin,
            'nogizaka46': self.nogizaka46_auth_plugin,
            'unknown': dummy_plugin,
            }[v]

        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:http://example.com', 'authz_identifier:http://example.com', 'membership:rakuten', 'membership_source:rakuten'])

        identities = {
            'fc_auth': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup' },
            'nogizaka46': {'membership': 'nogizaka46'},
            }
        result = target(identities, request)
        self.assertEqual(result, ['auth_identifier:test', 'authz_identifier:test', 'membership:test-membership', 'membership_source:fc_auth', 'membergroup:test-membergroup'])

        identities = {
            'nogizaka46': {'membership': 'nogizaka46'},
            'unknown': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup' },
            }
        result = target(identities, request)
        self.assertEqual(result, ['auth_identifier:test', 'authz_identifier:test', 'membership:test-membership', 'membership_source:unknown', 'membergroup:test-membergroup'])
        
    def test_priority_from_settings(self):
        identities = {
            'fc_auth': {'username': 'test', 'membership': 'test-membership', 'membergroup': 'test-membergroup' },
            'rakuten': {'claimed_id': 'http://example.com', 'membership': 'rakuten'},
            }
        request = testing.DummyRequest()

        self.plugin_registry.lookup = lambda v: {
            'fc_auth': self.fc_auth_plugin,
            'rakuten': self.rakuten_auth_plugin,
            }[v]

        self.config.registry.settings = {
            'altair.app.ticketing.security.auth_priorities': '''
                altair.rakuten_auth.openid.RakutenOpenID
                altair.app.ticketing.fc_auth.plugins.FCAuthPlugin
                ''',
            }
        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:http://example.com', 'authz_identifier:http://example.com', 'membership:rakuten', 'membership_source:rakuten'])
        
        self.config.registry.settings = {
            'altair.app.ticketing.security.auth_priorities': '''
                altair.rakuten_auth.openid.RakutenOpenID 1
                altair.app.ticketing.fc_auth.plugins.FCAuthPlugin
                ''',
            }
        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:test', 'authz_identifier:test', 'membership:test-membership', 'membership_source:fc_auth', 'membergroup:test-membergroup'])
        
        self.config.registry.settings = {
            'altair.app.ticketing.security.auth_priorities': '''
                altair.rakuten_auth.openid.RakutenOpenID
                altair.app.ticketing.fc_auth.plugins.FCAuthPlugin -1
                ''',
            }
        target = self._makeOne(self.config)
        result = target(identities, request)

        self.assertEqual(result, ['auth_identifier:test', 'authz_identifier:test', 'membership:test-membership', 'membership_source:fc_auth', 'membergroup:test-membergroup'])

