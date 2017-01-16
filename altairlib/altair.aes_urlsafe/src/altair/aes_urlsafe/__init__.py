# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from Crypto import Random
import base64

class AESURLSafe(object):
    def __init__(self):
        self.key = "THIS_IS_SECRET_KEY_FOR_QR_CODE!!"
        self.size = AES.block_size

    def __cipher(self, iv=None):
        if iv is None:
            iv = Random.new().read(AES.block_size)

        cipher = AES.new(self.key, AES.MODE_CFB, iv)
        return cipher, iv

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
        return ''.join(decrypted_list).strip().decode('utf-8')