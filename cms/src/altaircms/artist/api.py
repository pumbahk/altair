# -*- encoding:utf-8 -*-api.py

import base64
from Crypto import Random
from Crypto.Cipher import AES
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class AESCipher(object):
    def __init__(self, key, block_size=32):
        self.bs = block_size
        if len(key) >= len(str(block_size)):
            self.key = key[:block_size]
        else:
            self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def conv2datetime(timestr):
    try:
        return datetime.strptime(timestr, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None


def get_nowtimes(request, timesstr):
    try:
        aeskey = request.registry.settings.get("aes.artist.nowtime.secret.key")
        cipher = AESCipher(aeskey)
        nowtimestr = cipher.decrypt(timesstr)
        return conv2datetime(nowtimestr) if nowtimestr else None
    except Exception as e:
        logger.warning("failed to decrypt times %s", timesstr)
        return None


def get_encrypt(request, nowtimestr):
    try:
        if not conv2datetime(nowtimestr):
            return None

        aeskey = request.registry.settings.get("aes.artist.nowtime.secret.key")
        cipher = AESCipher(aeskey)
        return cipher.encrypt(nowtimestr)
    except Exception:
        return None
