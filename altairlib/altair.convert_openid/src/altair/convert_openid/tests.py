# -*- coding:utf-8 -*-
import unittest
import mock

from pyramid import testing

class ConvertOpenIDTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings = {
            'altair.converter_openid.endpoint': 'http://stg-api.id.db.rakuten.co.jp/openid_api/get_easy_id?openid=',
            'altair.converter_openid.timeout': 20
        }
        self.config.include('altair.convert_openid')

    def _callFUT(self, *args, **kwargs):
        from . import api
        return api.convert_openid_to_easyid(*args, **kwargs)

    def test_it(self):
        request = testing.DummyRequest()
        openid = 'https://myid.rakuten.co.jp/openid/user/rNmPCzshCVbzC2SulpKTnGlWg=='
        result = self._callFUT(
            request=request,
            openid=openid
        )

        # 期待値のeasyid
        expected_easyid = '13256346'
        self.assertEqual(result, expected_easyid)
