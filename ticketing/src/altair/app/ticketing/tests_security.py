import unittest

from pyramid import testing

class auth_model_callbackTests(unittest.TestCase):
    def setUp(self):
        self.fc_auth_plugin = self._get_fc_auth_plugin()('rememberer')
        self.rakuten_auth_plugin = self._get_rakuten_auth_plugin()('rememberer')

    def _get_fc_auth_plugin(self):
        from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin
        return FCAuthPlugin

    def _get_rakuten_auth_plugin(self):
        from altair.rakuten_auth.plugins import RakutenOpenIDPlugin
        return RakutenOpenIDPlugin

    def _callFUT(self, *args, **kwargs):
        from .security import auth_model_callback
        return auth_model_callback(*args, **kwargs)

    def test_non_dict(self):
        identity = ""
        request = testing.DummyRequest()

        result = self._callFUT(identity, request)

        self.assertEqual(result, [])

    def test_membership(self):
        identity = {'authenticator': self.fc_auth_plugin, 'identifier': self.fc_auth_plugin, 'membership': 'test-membership'}
        request = testing.DummyRequest()

        result = self._callFUT(identity, request)

        self.assertEqual(result, ['membership:test-membership', 'auth_type:fc_auth'])

    def test_membergroup(self):
        identity = {'authenticator': self.fc_auth_plugin, 'identifier': self.fc_auth_plugin, 'membergroup': 'test-membergroup'}
        request = testing.DummyRequest()

        result = self._callFUT(identity, request)

        self.assertEqual(result, ['membergroup:test-membergroup', 'auth_type:fc_auth'])
        
    def test_claimed_id(self):
        identity = {'authenticator': self.rakuten_auth_plugin, 'identifier': self.rakuten_auth_plugin, 'claimed_id': 'http://example.com'}
        request = testing.DummyRequest()

        result = self._callFUT(identity, request)

        self.assertEqual(result, ['auth_type:rakuten'])
