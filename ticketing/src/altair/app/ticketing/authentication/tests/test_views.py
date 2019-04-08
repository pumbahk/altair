# coding=utf-8
import unittest

from altair.oauth_auth.plugin import OAuthAuthPlugin
from pyramid.response import Response

from mock import patch

from altair.app.ticketing.authentication import PrivateKeyAuthView

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
