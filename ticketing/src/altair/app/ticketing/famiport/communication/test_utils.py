# -*- coding: utf-8 -*-
from unittest import TestCase
import urllib
import base64


class CryptoTest(TestCase):
    def _get_target(self):
        from .utils import Crypto as klass
        return klass

    def _make_one(self, *args, **kwds):
        klass = self._get_target()
        return klass(*args, **kwds)


class DecryptTest(CryptoTest):
    def _callFUT(self, key, value):
        import six
        from cryptography.hazmat.backends import default_backend
        from .utils import Crypto
        c = Crypto(default_backend())
        key = c.gen_key_from_special_field_value(key)
        iv = key
        rv_unquoted = urllib.unquote(value)
        rv_unquoted_decoded = base64.b64decode(rv_unquoted)
        plain_text = c.decrypt(rv_unquoted_decoded, key, iv)
        decrypted = six.text_type(plain_text, 'UTF-8')
        return decrypted

    def test_decrypt_data_1(self):
        val = self._callFUT('430000000002', 'vPdzNA1iUsC2fDTItw6C8w==')
        self.assertEqual(val, 'memberId432')

    def test_decrypt_data_2(self):
        val = self._callFUT('1000000000000', 'pT6fj7ULQklIfOWBKGyQ6g%3d%3d')
        self.assertEqual(val, u'ワ　ラ')

    def test_decrypt_data_3(self):
        val = self._callFUT('430000000002', '6ZkxFHNPaiaXzUH/LbkM/HgFScPtuyapgFOcNYYYSxE=')
        self.assertEqual(val, u'発券　し太郎')

    def test_decrypt_data_4(self):
        val = self._callFUT(
            '430000000002',
            'FYw9poK4AXcwknaFvLoXGgoCHZhMNBBNPTmV0qwQxxN0K2qUDUIVUjbwNSqKk1AL4K8GGseoY6cvoaOf8vhmq69Swp8s4UmjVva9XdPLuXy2orj9efTqyTh7O6AuZkUx')  # noqa
        self.assertEqual(val, u'神奈川県横浜市西区みなとみらい4-4-5 横浜アイマークプレイス')

    def test_decrypt_data_5(self):
        val = self._callFUT('430000000002', 'YUkUeJbHVa7zt0X3v1KnYAyuX+DBKbV8CDgOqeVElcMDY6hoGhqdhi6dp9gcLLWSlfXEY4bftl+8M0O59QPJsxJnGzQwUxIMexe5WpvrBRs=')
        self.assertEqual(val, u'大阪府大阪市淀川区宮原4丁目1番6号 アクロス新大阪14階')


class EncryptTest(CryptoTest):
    def _get_target(self):
        from .utils import Crypto as klass
        return klass

    def _make_one(self, *args, **kwds):
        klass = self._get_target()
        return klass(*args, **kwds)

    def _callFUT(self, key, value):
        from cryptography.hazmat.backends import default_backend
        c = self._make_one(default_backend())
        key = c.gen_key_from_special_field_value(key)
        iv = key
        value = value.encode('utf8')
        rv = c.encrypt(value, key, iv)
        rv = base64.b64encode(rv)
        # rv = urllib.quote(rv)
        return rv

    def test_encrypt_data_1(self):
        val = self._callFUT('430000000002', 'memberId432')
        self.assertEqual(val, 'vPdzNA1iUsC2fDTItw6C8w==')

    def test_encrypt_data_2(self):
        val = self._callFUT('1000000000000', u'ワ　ラ')
        self.assertEqual(val, 'pT6fj7ULQklIfOWBKGyQ6g==')

    def test_encrypt_data_3(self):
        val = self._callFUT('430000000002', u'発券　し太郎')
        self.assertEqual(val, '6ZkxFHNPaiaXzUH/LbkM/HgFScPtuyapgFOcNYYYSxE=')

    def test_encrypt_data_4(self):
        val = self._callFUT('430000000002', u'神奈川県横浜市西区みなとみらい4-4-5 横浜アイマークプレイス')
        self.assertEqual(val, 'FYw9poK4AXcwknaFvLoXGgoCHZhMNBBNPTmV0qwQxxN0K2qUDUIVUjbwNSqKk1AL4K8GGseoY6cvoaOf8vhmq69Swp8s4UmjVva9XdPLuXy2orj9efTqyTh7O6AuZkUx')  # noqa

    def test_encrypt_data_5(self):
        val = self._callFUT('430000000002', u'大阪府大阪市淀川区宮原4丁目1番6号 アクロス新大阪14階')

        self.assertEqual(val, 'YUkUeJbHVa7zt0X3v1KnYAyuX+DBKbV8CDgOqeVElcMDY6hoGhqdhi6dp9gcLLWSlfXEY4bftl+8M0O59QPJsxJnGzQwUxIMexe5WpvrBRs=')


class FamiPortCryptTest(TestCase):
    def _get_target_class(self):
        from .utils import FamiPortCrypt as klass
        return klass

    def _get_target(self, *args, **kwds):
        klass = self._get_target_class()
        return klass(*args, **kwds)

    def test_it(self):
        key = '430000000002'
        val = 'memberId432'

        target = self._get_target(key)
        cipher_text = target.encrypt(val)
        plain_text = target.decrypt(cipher_text)
        self.assertEqual(val, plain_text)

    def test_decrypt(self):
        key = '430000000002'
        val = 'vPdzNA1iUsC2fDTItw6C8w=='
        expval = 'memberId432'

        target = self._get_target(key)
        retval = target.decrypt(val)
        self.assertEqual(retval, expval)

    def test_encrypt(self):
        key = '430000000002'
        val = 'memberId432'
        expval = 'vPdzNA1iUsC2fDTItw6C8w=='

        target = self._get_target(key)
        retval = target.encrypt(val)
        self.assertEqual(retval, expval)

    def test_enc_dec(self):
        key = '430000000002'
        plain_org = u'テストテスト'.encode('utf8')
        target = self._get_target(key)
        chipher_res = target.encrypt(plain_org)
        plain_res = target.decrypt(chipher_res)
        self.assertEqual(plain_org, plain_res)
