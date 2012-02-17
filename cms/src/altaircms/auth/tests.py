# coding: utf-8
import unittest
from httplib2 import Response

from pyramid import testing
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPUnauthorized

from altaircms.tests import BaseTest


class OAuthSuccessMock(object):
    @staticmethod
    def request(url, method):
        response = Response({'status':302, 'location':'http://example.com/'})
        content = 'oauth_token=hogehoge&oauth_token_secret=fugahoge'
        return (response, content)


class OAuthFailureMock(object):
    @staticmethod
    def request(url, method):
        response = Response({'status':401}) # Unauthorized
        return (response, 'failure')


class OAuthCallbackMock(object):
    @staticmethod
    def request(url, method):
        response = Response({'status':200})
        content = 'user_id=1234&oauth_token=token&oauth_token_secret=secret'
        return (response, content)


class TestAuthView(BaseTest):
    def setUp(self):
        self.request = testing.DummyRequest()
        super(TestAuthView, self).setUp()

    def test_normal_views(self):
        """
        ログイン、ログアウトページのテスト
        """
        from altaircms.auth.views import login, logout

        resp = login(self.request)
        self.assertEqual(resp, {'message':''})

        resp = logout(self.request)
        self.assertTrue(isinstance(resp, HTTPFound))
        self.assertEqual(resp.location, 'http://example.com/')

    def test_oauth_entry(self):
        """
        OAuthの認証開始テスト
        SP側はスタブオブジェクトを渡してテストを行なっている
        """
        from altaircms.auth.views import OAuthLogin

        view = OAuthLogin(self.request, consumer_key='key', consumer_secret='secret', _stub_client=OAuthFailureMock)
        resp = view.oauth_entry()
        self.assertEqual(resp.status_int, 401)
        self.assertTrue(isinstance(resp, HTTPUnauthorized))

        view = OAuthLogin(
            self.request, consumer_key='key', consumer_secret='secret',
            authorize_url='http://example.com/authorize', _stub_client=OAuthSuccessMock
        )
        resp = view.oauth_entry()
        self.assertTrue(isinstance(resp, HTTPFound))
        self.assertEqual(resp.status_int, 302)
        self.assertTrue(resp.location.startswith('http://example.com/authorize'))

    def test_oauth_callback(self):
        """
        OAuthコールバックテスト
        SP側はスタブオブジェクトを渡してテストを行なっている
        """
        from altaircms.auth.views import OAuthLogin

        self.request.session['request_token'] = {
            'oauth_token':'token',
            'oauth_token_secret':'secret'
        }

        view = OAuthLogin(
            self.request, consumer_key='key', consumer_secret='secret',
            access_token_url='http://example.com/access_token', _stub_client=OAuthCallbackMock
        )
        resp = view.oauth_callback()
        self.assertTrue(isinstance(resp, HTTPFound))
        self.assertEqual(resp.location, '/')
