# -*- coding: utf-8 -*-
import base64
import unittest
import urllib
import urlparse
from binascii import unhexlify

from altair.app.ticketing.famiport.barcode_url.interfaces import IFamimaBarcodeUrlGeneratorFactory
from altair.app.ticketing.utils import Crypto

from pyramid import testing


class FamimaBarcodeURLTest(unittest.TestCase):
    def setUp(self):
        settings = {
            'altair.famima.cipher.pub_key': 'FE09C7B73C2C37DC8A4A3A555FCA6EB0',
            'altair.famima.cipher.iv': 'CE226A581D4A571C491A3A4957C0ED10',
            'altair.famima.barcode.url': 'https://ncpfa.famima.com/stg/ebcweb',
            'altair.famima.barcode.url.param.cp_no': '007',
            'altair.famima.barcode.url.param.gy_no': '04',
        }
        self.config = testing.setUp(settings=settings)
        self.config.include('altair.app.ticketing.famiport.barcode_url')

    def _decrypt(self, settings, e_key):
        pub_key = settings['altair.famima.cipher.pub_key']
        iv = settings['altair.famima.cipher.iv']
        # base64 デコードする
        decoded = self._decode(e_key)
        # AES128-CBC 方式で複合化する
        crypto = Crypto(unhexlify(pub_key), unhexlify(iv))
        return crypto.decrypt(decoded)

    def _decode(self, cipher_text):
        """Famima 指定の変換ルールを戻してデコードします
        """
        cipher_text = cipher_text + '=' * (65 - len(cipher_text))
        return base64.urlsafe_b64decode(cipher_text)

    def test_it(self):
        reserve_number = '1122334455667'
        print('Famima reserve_number: {}'.format(reserve_number))

        request = testing.DummyRequest()
        generator = request.registry.getUtility(IFamimaBarcodeUrlGeneratorFactory)
        barcode_url = generator.generate(reserve_number)
        print('Generated URL: {}'.format(barcode_url))

        settings = self.config.registry.settings
        url, query = urllib.splitquery(barcode_url)
        self.assertEqual(url, settings['altair.famima.barcode.url'])

        params = urlparse.parse_qs(query)

        self.assertEqual(params['cpNo'][0], settings['altair.famima.barcode.url.param.cp_no'])
        self.assertEqual(params['gyNo'][0], settings['altair.famima.barcode.url.param.gy_no'])

        decrypted = self._decrypt(settings, params['eKey'][0])
        print('Decrypted eKey: {}'.format(repr(decrypted)))

        # firstKey に予約番号、secondKey は null であることを確認
        self.assertTrue('firstKey={}&secondKey=\n'.format(reserve_number) == decrypted)
