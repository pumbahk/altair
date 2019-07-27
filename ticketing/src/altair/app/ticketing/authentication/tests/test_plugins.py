# coding=utf-8
import base64
import mock
import unittest
from binascii import unhexlify

from altair.app.ticketing.authentication.plugins import externalmember
from altair.app.ticketing.authentication.plugins.privatekey import PrivateKeyAuthPlugin, PRIVATEKEY_AUTH_IDENTIFIER_NAME
from altair.app.ticketing.utils import Crypto
from altair.oauth_auth.plugin import OAuthAuthPlugin
from pyramid import testing


class PrivateKeyAuthPluginTest(unittest.TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()

    def test_successful_authentication(self):
        mock_oauth_auth_plugin = mock.Mock()
        type(mock_oauth_auth_plugin).name = OAuthAuthPlugin.__name__
        mock_auth_context = mock.Mock()
        type(mock_auth_context).session_keepers = [mock_oauth_auth_plugin]

        expected_session_keeper = {
            PRIVATEKEY_AUTH_IDENTIFIER_NAME: {
                'keyword': 'testKey',
            }
        }

        auth_factors = {
            OAuthAuthPlugin.__name__: expected_session_keeper
        }

        expected_identity = {
            'username': '::privatekey::',
            'is_guest': True,
            'membership': 'privatekey',
        }

        mock_backend = mock.Mock(return_value=expected_identity)

        plugin = PrivateKeyAuthPlugin(mock_backend)

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

        plugin = PrivateKeyAuthPlugin(mock_backend)

        # identity が取得できない場合は (None, None) が取得されます
        identity, session_keeper = plugin.authenticate(self.request, mock_auth_context, auth_factors={})

        self.assertIsNone(identity)
        self.assertIsNone(session_keeper)


class ExternalMemberAuthPluginTest(unittest.TestCase):
    RAW_PARAMS = {
        'email_address': 'test@example.com',
        'member_id': '100',
        'keyword': 'testKey',
    }

    def setUp(self):
        # self.request = testing.DummyRequest()
        crypto = Crypto(unhexlify('8e1356089ccc232e4984cc2f02aee518'),
                        unhexlify('1c6514a594ffd8c649dd71ea1fcec3b3'))
        # 暗号化結果をPOSTデータにセット
        self.request = testing.DummyRequest(post={
            k: base64.b64encode(crypto.encrypt(v)) for k, v in self.RAW_PARAMS.items()
        })

    @mock.patch('{}.decide'.format(externalmember.__name__))
    def test_successful_authentication(self, mock_decide):
        mock_decide.return_value = [externalmember.EXTERNALMEMBER_AUTH_IDENTIFIER_NAME]

        mock_oauth_auth_plugin = mock.Mock()
        type(mock_oauth_auth_plugin).name = OAuthAuthPlugin.__name__
        mock_auth_context = mock.Mock()
        type(mock_auth_context).session_keepers = [mock_oauth_auth_plugin]

        expected_session_keeper = {externalmember.EXTERNALMEMBER_AUTH_IDENTIFIER_NAME: self.RAW_PARAMS}

        auth_factors = {
            OAuthAuthPlugin.__name__: expected_session_keeper
        }

        expected_identity = {
            'username': '::externalmember::',
            'is_guest': False,
            'membership': 'externalmember',
            'externalmember_email_address': self.RAW_PARAMS.get('email_address'),
            'externalmember_id': self.RAW_PARAMS.get('member_id')
        }

        mock_backend = mock.Mock(return_value=expected_identity)

        plugin = externalmember.ExternalMemberAuthPlugin(mock_backend)

        # identity が取得されるので、sessionにも保存される
        identity, session_keeper = plugin.authenticate(self.request, mock_auth_context, auth_factors)

        self.assertDictEqual(expected_identity, identity)
        self.assertDictEqual(expected_session_keeper, session_keeper[OAuthAuthPlugin.__name__])

    @mock.patch('{}.decide'.format(externalmember.__name__))
    def test_failed_authentication(self, mock_decide):
        mock_decide.return_value = [externalmember.EXTERNALMEMBER_AUTH_IDENTIFIER_NAME]

        mock_oauth_auth_plugin = mock.Mock()
        type(mock_oauth_auth_plugin).name = OAuthAuthPlugin.__name__
        mock_auth_context = mock.Mock()
        type(mock_auth_context).session_keepers = [mock_oauth_auth_plugin]

        mock_backend = mock.Mock(return_value=None)

        plugin = externalmember.ExternalMemberAuthPlugin(mock_backend)

        # identity が取得できない場合は (None, None) が取得されます
        identity, session_keeper = plugin.authenticate(self.request, mock_auth_context, auth_factors={})

        self.assertIsNone(identity)
        self.assertIsNone(session_keeper)

        self.request.POST['keyword'] = 'failure'
