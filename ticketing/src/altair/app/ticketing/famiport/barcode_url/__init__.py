# -*- coding: utf-8 -*-
import base64
import urllib

from binascii import unhexlify
from zope.interface import implementer

from altair.app.ticketing.famiport.barcode_url.interfaces import IFamimaBarcodeUrlGeneratorFactory
from altair.app.ticketing.famiport.utils import Crypto


@implementer(IFamimaBarcodeUrlGeneratorFactory)
class FamimaBarcodeUrlGeneratorFactory(object):
    """Famima 電子バーコードの URL を生成する
    """
    def __init__(self, pub_key, iv, base_url, cp_no, gy_no):
        """
        :param pub_key: 共通鍵
        :param iv: 初期化ベクトル
        :param base_url: Famima 電子バーコード URL
        :param cp_no: CP NO
        :param gy_no: 業務 NO
        """
        self.pub_key = pub_key
        self.iv = iv
        self.base_url = base_url
        self.cp_no = cp_no
        self.gy_no = gy_no

    def generate(self, reserve_number):
        """Famima 電子バーコード URL を生成
        :param reserve_number: Famima 予約番号
        :return: https://{famima url}?eKey={暗号化されたテキスト}&cpNo={CP番号}&gyNo={業務番号}
        """
        plain_text = 'firstKey={}&secondKey=\n'.format(reserve_number)
        crypto = Crypto()
        encrypted = crypto.encrypt(plain_text, unhexlify(self.pub_key), unhexlify(self.iv))
        encoded = base64.urlsafe_b64encode(encrypted).rstrip('=')  # '+' → '-', '/' → '_', '=' 削除
        params = (('eKey', encoded), ('cpNo', self.cp_no), ('gyNo', self.gy_no))
        url = '{}?{}'.format(self.base_url, urllib.urlencode(params))
        return url


def includeme(config):
    settings = config.registry.settings
    pub_key = settings.get('altair.famima.cipher.pub_key')
    iv = settings.get('altair.famima.cipher.iv')
    base_url = settings.get('altair.famima.barcode.url')
    cp_no = settings.get('altair.famima.barcode.url.param.cp_no')
    gy_no = settings.get('altair.famima.barcode.url.param.gy_no')
    factory = FamimaBarcodeUrlGeneratorFactory(pub_key, iv, base_url, cp_no, gy_no)
    config.registry.registerUtility(factory, IFamimaBarcodeUrlGeneratorFactory)
