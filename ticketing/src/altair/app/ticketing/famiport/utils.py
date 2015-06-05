# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from xml.etree import ElementTree
from xml.dom import minidom

import urllib
from cryptography.hazmat.backends import default_backend

import six
import base64
from cryptography.hazmat.primitives import hashes, ciphers, padding
from cryptography.hazmat.primitives.ciphers import algorithms, modes


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


class YAFamiPortCrypt(object):
    def __init__(self, special_field_value, encoding='utf8'):
        self._core = Crypto()
        self.key = self._core.gen_key_from_special_field_value(special_field_value)
        self.encoding = encoding

    @property
    def iv(self):
        return self.key

    def decrypt(self, value):
        value = urllib.unquote(value)
        value = base64.b64decode(value)
        value = self._core.decrypt(value, self.key, self.iv)
        value = six.text_type(value, self.encoding)
        return value

    def encrypt(self, value):
        value = self._core.encrypt(value, self.key, self.iv)
        value = base64.b64encode(value)
        value = urllib.quote(value)
        value = value.encode('utf8')
        return value


class FamiPortCrypt(object):
    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt(self, plain_data):
        """
        Encrypt plain_data with the given key in init
        :param plain_data:
        :return: encrypted data
        """

        return self.fernet.encrypt(plain_data)

    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted_data with the given key in init
        :param encrypted data:
        :return: decrypted data
        """

        return self.fernet.decrypt(encrypted_data)


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
