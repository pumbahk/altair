# coding=utf-8
import base64
import unittest

from altair.app.ticketing.utils import Crypto
from pyramid.testing import setUp

from altair.oauth_auth.plugin import OAuthAuthPlugin
from pyramid import testing
from pyramid.response import Response

from mock import patch

from altair.app.ticketing.authentication.interfaces import IExternalMemberAuthCrypto
from altair.app.ticketing.authentication.views import PrivateKeyAuthView, ExternalMemberAuthView

TEST_KEY = 'testKey'
auth_key_dict = {'key': TEST_KEY}


def make_request():
    class Request(object):
        method = 'POST'
        response = Response()
        POST = {'keyword': TEST_KEY}

        def current_route_path(self):
            return 'current route path'

    return Request()


class TicketingKeyBaseAuthViewTest(unittest.TestCase):
    def setUp(self):
        self.request = make_request()

    @property
    def identities(self):
        return {
            'privatekey': {
                'username': '::privatekey::',
                'is_guest': True,
                'membership': 'privatekey'
            }
        }

    @property
    def auth_factors(self):
        return {
            OAuthAuthPlugin.__name__: {'privatekey': auth_key_dict},
            'pyramid_session:altair.auth.pyramid': {'privatekey': auth_key_dict}
        }

    @property
    def headers(self):
        return {
            OAuthAuthPlugin.__name__: {'privatekey': auth_key_dict},
            'pyramid_session:altair.auth.pyramid': {'privatekey': auth_key_dict}
        }

    def test_already_authenticated(self):
        with patch('altair.app.ticketing.authentication.views.get_who_api') as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (self.identities, self.auth_factors, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            view = PrivateKeyAuthView(self.request)
            view()

            # 既に認証済みでセッションに残っているので login はコールされていないことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_not_called()

    def test_login(self):
        with patch('altair.app.ticketing.authentication.views.get_who_api') as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (None, None, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            view = PrivateKeyAuthView(self.request)
            view()

            # 未認証で identities が取得できなかったので、login による新規認証がコールされたことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_called_once_with(credentials={'privatekey': auth_key_dict})


class ExternalMemberAuthViewTest(unittest.TestCase):
    def setUp(self):
        from binascii import unhexlify
        crypto = Crypto(unhexlify('8e1356089ccc232e4984cc2f02aee518'), unhexlify('1c6514a594ffd8c649dd71ea1fcec3b3'))
        self.raw_keyword_val = 'ASf44frt'
        encrypted = crypto.encrypt(self.raw_keyword_val)
        # 暗号化結果をPOSTデータにセット
        self.request = testing.DummyRequest(post={'keyword': base64.b64encode(encrypted)})
        self.config = setUp(request=self.request)
        self.request.registry.registerUtility(crypto, IExternalMemberAuthCrypto)

    def test_decrypt(self):
        view = ExternalMemberAuthView(self.request)
        encrypted = view.get_credential('keyword')
        # 復号化結果が元の値と同じであることを確認
        self.assertEqual(self.raw_keyword_val, encrypted)
