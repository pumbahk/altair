# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from Crypto import Random
import base64

DEFAULT_KEY = "!ALTAIR_AES_ENCRYPTION_URL_SAFE!"

class SecretKeyException(Exception):
    pass

class AESURLSafe(object):
    def __init__(self, key=None):
        self.key = key or DEFAULT_KEY
        self.size = AES.block_size

    def __cipher(self, iv=None):
        if iv is None:
            iv = Random.new().read(AES.block_size)

        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher, iv

    def update_key(self, key):
        self.key = key

    def encrypt(self, s):
        s = s.encode('utf-8')
        if len(s) % self.size != 0:
            s += ' ' * (self.size - len(s) % self.size)

        encrytable_list = [s[i:i + self.size] for i in range(0, len(s), self.size)]
        cipher, iv = self.__cipher()
        encrypted_list = map(cipher.encrypt, encrytable_list)
        token = iv + ''.join(encrypted_list)
        return base64.urlsafe_b64encode(token)

    def decrypt(self, s):
        token = base64.urlsafe_b64decode(s)
        iv = token[:self.size]
        s = token[self.size:]
        decryptable_list = [s[i:i + self.size] for i in range(0, len(s), self.size)]
        cipher, iv = self.__cipher(iv)
        decrypted_list = map(cipher.decrypt, decryptable_list)
        try:
            # 違う秘密キーで復号した文字列はUTF-8にdecodeできない
            return ''.join(decrypted_list).strip().decode('utf-8')
        except UnicodeDecodeError:
            raise SecretKeyException('The secret key is different from that used to encrypt')
