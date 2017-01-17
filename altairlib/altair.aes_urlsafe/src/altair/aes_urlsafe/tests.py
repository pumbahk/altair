# -*- coding: utf-8 -*-
import unittest
from . import AESURLSafe, SecretKeyException

class AESToolTest(unittest.TestCase):
    qr_data = {
        "reco_code": "XXXXXXXXXX",
        "type": "3",
        "ticket_code": "401213",
        "serial_no": "00003665574684001",
        "issued_at": "20120327",
        "count_flag": "1",
        "season_flag": "1",
        "valid_from": "00000000",
        "valid_to": "00000000",
        "enter_limit": "0",
        "enter_tiem": "0000",
        "period_of_use": "00000000",
        "special_flag": "0",
    }

    def setUp(self):
        self.custom_key = "!THIS_KEY_IS_FOR_THE_UNIT_TESTS!"
        self.aes = AESURLSafe()
        self.aes_key = AESURLSafe(self.custom_key)


    def test_aes_kanji(self):
        self.assertEquals(self.aes.decrypt(self.aes.encrypt(u"あいう")), u"あいう")


    def test_aes_key_kanji(self):
        self.assertEquals(self.aes_key.decrypt(self.aes_key.encrypt(u"あいう")), u"あいう")


    def test_aes_asc(self):
        self.assertEquals(self.aes.decrypt(self.aes.encrypt(u"ABC")), u"ABC")


    def test_aes_key_asc(self):
        self.assertEquals(self.aes_key.decrypt(self.aes_key.encrypt(u"ABC")), u"ABC")


    def test_aes_arbitrary(self):
        s = u"A あa!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ん"
        self.assertEquals(self.aes.decrypt(self.aes.encrypt(s)), s)


    def test_aes_key_arbitrary(self):
        s = u"A あa!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ん"
        self.assertEquals(self.aes_key.decrypt(self.aes_key.encrypt(s)), s)


    def test_aes_qr_data(self):
        from collections import OrderedDict
        data = OrderedDict(self.qr_data)
        s = u"".join([v for k, v in data.items()])
        self.assertEquals(self.aes.decrypt(self.aes.encrypt(s)), s)


    def test_aes_key_qr_data(self):
        from collections import OrderedDict
        data = OrderedDict(self.qr_data)
        s = u"".join([v for k, v in data.items()])
        self.assertEquals(self.aes_key.decrypt(self.aes_key.encrypt(s)), s)


    def test_aes_with_different_object(self):
        new_aes = AESURLSafe()
        self.assertEquals(new_aes.decrypt(self.aes.encrypt(u"ABC")), u"ABC")


    def test_aes_key_with_different_object(self):
        new_aes = AESURLSafe(self.custom_key)
        self.assertEquals(new_aes.decrypt(self.aes_key.encrypt(u"ABC")), u"ABC")


    def test_aes_key_with_different_object_fail(self):
        new_aes = AESURLSafe("ABCDEFGHABCDEFGHABCDEFGHABCDEFGH")
        self.assertRaises(SecretKeyException, new_aes.decrypt, (self.aes_key.encrypt(u"ABC")))


    def test_aes_update_key(self):
        new_aes = AESURLSafe()
        new_aes.update_key(self.custom_key)
        self.assertEquals(new_aes.decrypt(self.aes_key.encrypt(u"ABC")), u"ABC")