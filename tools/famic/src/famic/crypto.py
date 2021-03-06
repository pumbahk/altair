# -*- coding: utf-8 -*-
import six
import urllib
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import (
    hashes,
    ciphers,
    padding,
    )
from cryptography.hazmat.primitives.ciphers import (
    algorithms,
    modes,
    )


class Crypto(object):

    def md5_hash(self, data):
        hasher = hashes.Hash(hashes.MD5(), backend=self.backend)
        hasher.update(data)
        return hasher.finalize()

    def pad(self, data):
        p = padding.PKCS7(128).padder()
        return p.update(data) + p.finalize()

    def unpad(self, data):
        p = padding.PKCS7(128).unpadder()
        return p.update(data) + p.finalize()

    def encrypt(self, data, key, iv):
        c = ciphers.Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        e = c.encryptor()
        return e.update(self.pad(data)) + e.finalize()

    def decrypt(self, data, key, iv):
        c = ciphers.Cipher(algorithms.AES(key), modes.CBC(iv), backend=self.backend)
        e = c.decryptor()
        return self.unpad(e.update(data) + e.finalize())

    def gen_key_from_special_field_value(self, v):
        return b''.join(b'%02x' % six.byte2int(c) for c in self.md5_hash(v.encode('ASCII')))[0:16]

    def __init__(self, backend=None):
        self.backend = backend if backend is not None else default_backend()


class KusoCrypto(object):
    def __init__(self, special_field_value, encoding='utf8'):
        self._core = Crypto()
        self.key = self._core.gen_key_from_special_field_value(special_field_value)
        self.encoding = encoding

    @property
    def iv(self):
        return self.key

    def encrypt(self, plain_data):
        value = plain_data
        value = self._core.encrypt(value, self.key, self.iv)
        value = base64.b64encode(value)
        value = value.encode('utf8')
        return value

    def decrypt(self, encrypted_data):
        value = encrypted_data
        value = urllib.unquote(value)
        value = base64.b64decode(value)
        value = self._core.decrypt(value, self.key, self.iv)
        return value
