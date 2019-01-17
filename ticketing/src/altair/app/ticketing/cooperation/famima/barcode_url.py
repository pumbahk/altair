# -*- coding: utf-8 -*-
import base64
import urllib

from Crypto.Cipher import AES
from zope.interface import implementer

from .interfaces import IFamimaURLGeneratorFactory


@implementer(IFamimaURLGeneratorFactory)
class FamimaURLGeneratorFactory(object):
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
        plain_text = urllib.urlencode((('firstKey', reserve_number), ('secondKey', '')))
        cipher = FamimaURLAESCipher(self.pub_key, self.iv)
        encrypted = cipher.encrypt(plain_text)
        params = (('eKey', encrypted), ('cpNo', self.cp_no), ('gyNo', self.gy_no))
        url = '{}?{}'.format(self.base_url, urllib.urlencode(params))
        return url


class FamimaURLAESCipher(object):
    """AES128-CBC 方式で暗号化を行います
    """
    def __init__(self, key, iv):
        self.cipher = AES.new(key, AES.MODE_CBC, iv)

    def encrypt(self, plain_text):
        """
        暗号化を行います。電子バーコード URL のリクエストパラメーター eKey の値となります。
        暗号化するテキストの形式は firstKey={ファミマ予約番号}&secondKey={NULL}

        公開鍵暗号標準 PKCS#5 でパディング
        　　　　　　↓
        AES128-CBC 方式で暗号化
        　　　　　　↓
        Base64 エンコーディング
        """
        padded = self.pad(plain_text)
        cipher_text = self.cipher.encrypt(padded)
        encoded = self.encode(cipher_text)
        return encoded

    def pad(self, data_to_pad):
        """公開鍵暗号標準 PKCS#5 パディング処理
        AES_CBC はテキストの長さが AES.block_size の倍数でなければならないのでパディング処理で長さを調節します。
        """
        padding_len = AES.block_size - len(data_to_pad) % AES.block_size
        padding = chr(padding_len) * padding_len
        return data_to_pad + padding

    def encode(self, cipher_text):
        """Famima指定のルールで暗号化テキストを Base64 エンコーディング
        - '+' を '-' に変換
        - '/' を '_' に変換
        - '=' を削除
        """
        encoded = base64.b64encode(cipher_text, '-_')
        return encoded.replace('=', '')


def includeme(config):
    settings = config.registry.settings
    pub_key = settings.get('altair.famima.cipher.pub_key')
    iv = settings.get('altair.famima.cipher.iv')
    base_url = settings.get('altair.famima.barcode.url')
    cp_no = settings.get('altair.famima.barcode.url.param.cp_no')
    gy_no = settings.get('altair.famima.barcode.url.param.gy_no')
    factory = FamimaURLGeneratorFactory(pub_key, iv, base_url, cp_no, gy_no)
    config.registry.registerUtility(factory, IFamimaURLGeneratorFactory)
