# -*- coding:utf-8 -*-

import unittest
import mock

from pyramid.testing import DummyRequest, DummyModel

class FanclubAuthPluginTests(unittest.TestCase):
    """
    plugin.authenticate(self, request, auth_context, auth_factors)
        input
            request
            auth_context (AuthAPI)
            auth_factor  (
                "pollux": {
                    "altair.fanclub_auth.plugin.params": {}, <- received_params(after user authz: request_token, request_verifier, request_secret)
                    "altair.fanclub_auth.plugin.raw_identifier": {}, <- stored_identity(when on_extra_verify: stored in session)
                    "pyramid_session:altair.fanclub": {} <- identity
                })

        side effects
            remove cache key="oauth_request_token"
            add metadata(extra info) to request.environ <- why?
            add identity to request.environ <- why?

            try getting access token
            try getting member info from outside api

        output
            None, None  -> when received params are invalid
                        -> when 'verifier' not in identity
                        -> when failed to get extra info
            identity, auth_factors
    """

    def setUp(self):
        from .plugin import FanclubAuthPlugin, FanclubAuthURLBuilder, FanclubAuthHTTPSessionFactory
        from altair.app.ticketing.extauth.fanclub_auth import FanclubEndpointBuilder
        self.plugin = FanclubAuthPlugin(
            plugin_name="pollux",
            cache_region=None,
            endpoint_builder=FanclubEndpointBuilder(),
            url_builder=FanclubAuthURLBuilder(),
            consumer_key='keyxxxxxxxxxx',
            consumer_secret='secretxxxxxxx',
            session_factory=None,
            timeout=3600,
            oauth_scope=None,
            challenge_success_callback=None
            )

    def _callFUT(self, *args, **kwargs):
        return self.plugin.authenticate(*args, **kwargs)

    def _get_dummy_member_data(self):
        return dict(
            member_id='TEST000001',
            first_name=u'てすと',
            first_name_kana=u'テスト',
            last_name=u'楽天',
            last_name_kana=u'ラクテン',
            sex=u'1',
            fax=u'012033334444',
            birthday=u'1985-09-25',
            email_1=u'test@test.teeeeest',
            tel_1=u'0120999988888',
            tel_2=u'08099997777',
            zip=u'1030001',
            prefecture=u'13',
            city=u'世田谷区',
            address_1=u'ホゲホゲ町１−１',
            address_2=u'',
            memberships=[]
        )

    @mock.patch('altair.fanclub_auth.plugin.FanclubAuthPlugin._get_extras')
    @mock.patch('altair.fanclub_auth.plugin.FanclubAuthPlugin._get_cache')
    @mock.patch('beaker.cache.Cache.get')
    def test_it(self, _get_extras, _get_cache, cache_get):
        from beaker.cache import Cache
        request = DummyRequest()
        request.session.id = 123456789
        auth_context = mock.MagicMock(session_keepers=[DummyModel(name='pyramid_session:altair.fanclub')])
        auth_factors = {
            "pollux": {
                "altair.fanclub_auth.plugin.params": {
                    "oauth_verifier": "xxxxxxxx",
                    "oauth_request_token": "yyyyyyyy",
                    "oauth_request_secret": "zzzzzzzz"
                },
                "altair.fanclub_auth.plugin.raw_identifier": {},
                "pyramid_session:altair.fanclub": {}
            }
        }
        _get_extras.return_value = self._get_dummy_member_data()
        _get_cache.return_value = Cache('namespace')
        cache_get.return_value = self._get_dummy_member_data()
        identity, auth_factors = self._callFUT(request, auth_context, auth_factors)
        self.assertEqual('pollux_member_id' in identity, True)
        self.assertEqual('pyramid_session:altair.fanclub' in auth_factors, True)
