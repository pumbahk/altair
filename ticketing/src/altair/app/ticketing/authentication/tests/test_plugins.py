# coding=utf-8
import unittest

import mock
from altair.app.ticketing.authentication.plugins import TicketingKeyBaseAuthPlugin
from altair.app.ticketing.authentication.plugins.externalmember import EXTERNALMEMBER_AUTH_IDENTIFIER_NAME
from altair.app.ticketing.authentication.plugins.privatekey import PRIVATEKEY_AUTH_IDENTIFIER_NAME
from altair.oauth_auth.plugin import OAuthAuthPlugin
from pyramid import testing


class TicketingKeyBaseAuthPluginTest(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()

    def test_successful_authentication(self):
        mock_oauth_auth_plugin = mock.Mock()
        type(mock_oauth_auth_plugin).name = OAuthAuthPlugin.__name__
        mock_auth_context = mock.Mock()
        type(mock_auth_context).session_keepers = [mock_oauth_auth_plugin]

        expected_session_keeper = {
            EXTERNALMEMBER_AUTH_IDENTIFIER_NAME: {
                'email_address': 'test@example.com',
                'member_id': '100',
                'key': 'testKey',
            }
        }

        auth_factors = {
            OAuthAuthPlugin.__name__: expected_session_keeper
        }

        expected_identity = {
            'username': '::externalmember::',
            'is_guest': False,
            'membership': 'externalmember',
            'externalmember_email_address': 'test@example.com',
            'externalmember_id': '1'
        }

        mock_backend = mock.Mock(return_value=expected_identity)

        plugin = TicketingKeyBaseAuthPlugin(mock_backend)
        plugin.name = EXTERNALMEMBER_AUTH_IDENTIFIER_NAME

        # identity が取得されるので、sessionにも保存される
        identity, session_keeper = plugin.authenticate(self.request, mock_auth_context, auth_factors)

        self.assertDictEqual(expected_identity, identity)
        self.assertDictEqual(expected_session_keeper, session_keeper[OAuthAuthPlugin.__name__])

    def test_failed_authentication(self):
        mock_oauth_auth_plugin = mock.Mock()
        type(mock_oauth_auth_plugin).name = OAuthAuthPlugin.__name__
        mock_auth_context = mock.Mock()
        type(mock_auth_context).session_keepers = [mock_oauth_auth_plugin]

        mock_backend = mock.Mock(return_value=None)

        plugin = TicketingKeyBaseAuthPlugin(mock_backend)
        plugin.name = PRIVATEKEY_AUTH_IDENTIFIER_NAME

        # identity が取得できない場合は (None, None) が取得されます
        identity, session_keeper = plugin.authenticate(self.request, mock_auth_context, auth_factors={})

        self.assertIsNone(identity)
        self.assertIsNone(session_keeper)
