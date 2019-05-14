# coding=utf-8
import base64
import unittest
from binascii import unhexlify

from altair.app.ticketing.utils import Crypto
from pyramid.testing import setUp

from altair.oauth_auth.plugin import OAuthAuthPlugin
from pyramid import testing
from pyramid.response import Response

from mock import patch

from altair.app.ticketing.authentication.interfaces import IExternalMemberAuthCrypto
from altair.app.ticketing.authentication.plugins import externalmember, privatekey


class TicketingKeyBaseAuthComponent(object):
    auth_name = ''
    credential = {}

    @property
    def identities(self):
        return {
            self.auth_name: {
                'username': '::{}::'.format(self.auth_name),
                'is_guest': True,
                'membership': self.auth_name
            }
        }

    @property
    def auth_factors(self):
        return {
            OAuthAuthPlugin.__name__: {self.auth_name: self.credential},
            'pyramid_session:altair.auth.pyramid': {self.auth_name: self.credential}
        }

    @property
    def headers(self):
        return {
            OAuthAuthPlugin.__name__: {self.auth_name: self.credential},
            'pyramid_session:altair.auth.pyramid': {self.auth_name: self.credential}
        }


class PrivateKeyAuthPredicateTest(unittest.TestCase, TicketingKeyBaseAuthComponent):
    auth_name = 'privatekey'
    credential = {'keyword': 'testKey'}

    def setUp(self):
        self.request = testing.DummyRequest(post=self.credential)
        self.config = setUp(request=self.request)
        self.context = testing.DummyResource()

    @patch('{}.decide'.format(privatekey.__name__))
    def test_already_authenticated(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(privatekey.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (self.identities, self.auth_factors, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            predicate = privatekey.PrivateKeyAuthPredicate('keyword', self.config)
            res = predicate(self.context, self.request)

            self.assertTrue(res)

            # 既に認証済みでセッションに残っているので login はコールされていないことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_not_called()

    @patch('{}.decide'.format(privatekey.__name__))
    def test_login(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(privatekey.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (None, None, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            predicate = privatekey.PrivateKeyAuthPredicate('keyword', self.config)
            res = predicate(self.context, self.request)

            self.assertTrue(res)

            # 未認証で identities が取得できなかったので、login による新規認証がコールされたことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_called_once_with(credentials={'privatekey': self.credential})

    @patch('{}.decide'.format(privatekey.__name__))
    def test_login_failed(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(privatekey.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (None, None, {})
            api.login.return_value = (None, self.headers, {}, Response())
            predicate = privatekey.PrivateKeyAuthPredicate('keyword', self.config)
            res = predicate(self.context, self.request)

            # ログインに成功しなかったので predicate 結果は false であることを確認
            self.assertFalse(res)

            # 未認証で identities が取得できなかったので、login による新規認証がコールされたことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_called_once_with(credentials={'privatekey': self.credential})


class ExternalMemberAuthPredicateTest(unittest.TestCase, TicketingKeyBaseAuthComponent):
    auth_name = 'externalmember'
    credential = {
        'keyword': 'ASf44frt',
        'member_id': '1',
        'email_address': 'test@example.com'
    }

    def setUp(self):
        crypto = Crypto(unhexlify('8e1356089ccc232e4984cc2f02aee518'), unhexlify('1c6514a594ffd8c649dd71ea1fcec3b3'))

        # 暗号化結果をPOSTデータにセット
        self.request = testing.DummyRequest(post={
            k: base64.b64encode(crypto.encrypt(v)) for k, v in self.credential.items()
        })
        self.config = setUp(request=self.request)
        self.request.registry.registerUtility(crypto, IExternalMemberAuthCrypto)
        self.context = testing.DummyResource()

    @patch('{}.decide'.format(externalmember.__name__))
    def test_already_authenticated(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(externalmember.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (self.identities, self.auth_factors, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            predicate = externalmember.ExternalMemberAuthPredicate(('keyword', 'member_id', 'email_address'),
                                                                   self.config)
            res = predicate(self.context, self.request)

            self.assertTrue(res)

            # 既に認証済みでセッションに残っているので login はコールされていないことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_not_called()

    @patch('{}.decide'.format(externalmember.__name__))
    def test_login(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(externalmember.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (None, None, {})
            api.login.return_value = (self.identities, self.headers, {}, Response())
            predicate = externalmember.ExternalMemberAuthPredicate(('keyword', 'member_id', 'email_address'),
                                                                   self.config)
            res = predicate(self.context, self.request)

            self.assertTrue(res)

            # 未認証で identities が取得できなかったので、login による新規認証がコールされたことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_called_once_with(credentials={'externalmember': self.credential})

    @patch('{}.decide'.format(externalmember.__name__))
    def test_login_failed(self, mock_decide):
        mock_decide.return_value = [self.auth_name]
        with patch('{}.get_who_api'.format(externalmember.__name__)) as mock_api:
            api = mock_api.return_value
            api.authenticate.return_value = (None, None, {})
            api.login.return_value = (None, self.headers, {}, Response())
            predicate = externalmember.ExternalMemberAuthPredicate(('keyword', 'member_id', 'email_address'),
                                                                   self.config)
            res = predicate(self.context, self.request)

            # ログインに成功しなかったので predicate 結果は false であることを確認
            self.assertFalse(res)

            # 未認証で identities が取得できなかったので、login による新規認証がコールされたことを確認
            api.authenticate.assert_called_once_with()
            api.login.assert_called_once_with(credentials={'externalmember': self.credential})
