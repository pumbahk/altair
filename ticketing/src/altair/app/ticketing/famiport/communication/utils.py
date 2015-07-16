# -*- coding: utf-8 -*-
import urllib
import base64

import six

from xml.dom import minidom
from xml.etree import ElementTree

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
import jctconv


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


class FamiPortCrypt(object):
    def __init__(self, special_field_value, encoding='utf8'):
        self._core = Crypto()
        self.key = self._core.gen_key_from_special_field_value(special_field_value)
        self.encoding = encoding

    @property
    def iv(self):
        return self.key

    def encrypt(self, plain_data):
        """Encrypt plain_data with the given key in init

        :param plain_data:
        :return: encrypted data
        """
        value = plain_data.encode(self.encoding)
        value = self._core.encrypt(value, self.key, self.iv)
        value = base64.b64encode(value)
        return value

    def decrypt(self, encrypted_data):
        """Decrypt encrypted_data with the given key in init

        :param encrypted data:
        :return: decrypted data
        """
        value = encrypted_data
        value = urllib.unquote(value)
        value = base64.b64decode(value)
        value = self._core.decrypt(value, self.key, self.iv).decode(self.encoding)
        return value


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def str_or_blank(val, padding_count=0, fillvalue='', left=False):
    val = '' if val is None else unicode(val)
    if padding_count:
        ch = '<' if left else '>'
        fmt = '{}:{}{}{}{}'.format('{', fillvalue, ch, padding_count, '}')
        val = fmt.format(val)
    return val


def hankaku2zenkaku(text):
    """半角英数字を全角に変換する
    """
    return jctconv.h2z(text, digit=True, ascii=True)


def convert_famiport_kogyo_name_style(text, zenkaku=False, length=40, encoding='cp932', length_error=False):
    """FamiPort用興行名変換処理"""
    if zenkaku:
        text = hankaku2zenkaku(text)
    buf = text.encode(encoding)
    if len(buf) > length and length_error:
        raise ValueError('too long: {}'.format(text))
    for ii in range(len(buf)):
        try:
            return buf[:40-ii].decode(encoding)
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    assert False, text


def validate_convert_famiport_kogyo_name_style(*args, **kwds):
    kwds['length_error'] = True
    try:
        convert_famiport_kogyo_name_style(*args, **kwds)
        return True
    except Exception:
        return False
