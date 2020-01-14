# coding=utf-8
import base64
import unittest

from altair.app.ticketing.extauth.rakuten_auth import get_open_id_for_sso
from pyramid import testing

from Crypto.Cipher import AES


class TsCookieForSSOTest(unittest.TestCase):
    def setUp(self):
        self.key = 'raku10ticketstar'  # 暗号化キー
        self.iv = 'PMHthiiACFyBC9iB'  # 初期化ベクトル：16byteのランダム文字列
        self.config = testing.setUp(settings={'altair.rakuten_sso.ts.encryption_key': self.key})

    @staticmethod
    def _pad(s):
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)

    @staticmethod
    def _make_request(ts):
        return testing.DummyRequest(cookies={'Ts': ts})

    def _make_ts(self, open_id, mode=AES.MODE_CBC):
        cipher = AES.new(key=self.key, mode=mode, IV=self.iv)
        encrypted = cipher.encrypt(self._pad(open_id))
        encoded = base64.b64encode(encrypted)
        # Ts Cookie は初期化ベクトル + 暗号化した Open ID をbase64エンコードした文字列
        return self.iv + encoded

    def test_get_open_id_from_ts_cookie(self):
        """Ts Cookie から復号化して Open ID を取得"""
        open_id = 'https://myid.rakuten.co.jp/openid/user/EIekrdfO394873sqWow=='
        request = self._make_request(ts=self._make_ts(open_id=open_id))
        self.assertEqual(open_id, get_open_id_for_sso(request))

        open_id = 'https://myid.rakuten.co.jp/openid/user/qAe3rdf5123473Aiuew7ow=='
        request = self._make_request(ts=self._make_ts(open_id=open_id))
        self.assertEqual(open_id, get_open_id_for_sso(request))

    def test_get_no_open_id_from_invalid_ts_cookie(self):
        """Ts Cookie から Open ID を取得失敗"""
        # Ts Cookie が空
        request = self._make_request(ts='')
        self.assertIsNone(get_open_id_for_sso(request))

        # Ts Cookie の Open ID が空
        request = self._make_request(ts=self.iv + '')
        self.assertIsNone(get_open_id_for_sso(request))

        # Ts Cookie の Open ID が不正な値
        request = self._make_request(ts=self.iv + 'aaa')
        self.assertIsNone(get_open_id_for_sso(request))

        # Ts Cookie の Open ID が正しくない暗号化
        open_id = 'https://myid.rakuten.co.jp/openid/user/qAe3rdf5123473Aiuew7ow=='
        request = self._make_request(ts=self._make_ts(open_id=open_id, mode=AES.MODE_ECB))
        self.assertIsNone(get_open_id_for_sso(request))
