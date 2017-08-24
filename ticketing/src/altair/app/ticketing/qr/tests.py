# -*- coding: utf-8 -*-

import unittest
from .builder import qr, qr_aes
from .builder import InvalidItemList

class QrTest(unittest.TestCase):
    data = { "serial": "SERIALNUMBER",
             "performance": "PERFORMANCE",
             "order": "ORDERNUMBER",
             "date": "20120805",
             "type": 666,
             'seat': '$6V$7B$63$7.%Q0-A*H.-10', ## これは利用していないデータらしい, parseしたときに生じる
             "seat_name": u"ポンチョ席-A列-10",
             }
    
    def setUp(self):
        self.o = qr()
        self.o.key = "ticketstar"

    def tearDown(self):
        pass
    
    def test_enc32(self):
        self.assertEqual(self.o.dec32(self.o.enc32(31)), 31)

    def test_enc42(self):
        s = u"A あa!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ん"
        self.assertEqual(self.o.dec42(self.o.enc42(s)), s)

    def test_enc42_basic(self):
        self.assertEqual(self.o.dec42(self.o.enc42(u"あいう")), u"あいう")

    def test_enc42_euc_mark(self):
        self.assertEqual(self.o.dec42(self.o.enc42(u"△■＠")), u"△■＠")

    def test_enc42_utf_mark_replace(self):
        self.assertEqual(self.o.dec42(self.o.enc42(u"♡")), u"〓")

    def test_enc42_asc(self):
        self.assertEqual(self.o.dec42(self.o.enc42("ABC")), u"ABC")

    def test_enc42_misc(self):
        self.assertEqual(self.o.dec42(self.o.enc42("abc")), u"abc")

    def test_sign(self):
        self.assertEqual(self.o.sign("ABC"), "CP7BJVI7"+"ABC")
    
    def test_validate_sign(self):
        self.assertTrue(self.o.validate(self.o.sign("ABC")))
    
    def test_make_sample_1(self):
        self.assertEqual(self.o.sign(self.o.make(self.data)),
                         "GRKAKLS1HSSERIALNUMBERRRPERFORMANCEQRORDERNUMBERSK0S85TJ29QU1N$6V$7B$63$7.%Q0-A*H.-10")
    
    def test_make_and_parse(self):
        self.assertEqual(self.o.parse(self.o.make(self.data)), self.data)


    def test_data_from_signed(self):
        signed = self.o.sign(self.o.make(self.data))
        self.assertEqual(self.o.data_from_signed(signed), self.data)

    def test_data_from_signed_with_invalid_sign(self):
        from altair.app.ticketing.qr import InvalidSignedString

        signed = self.o.sign(self.o.make(self.data))
        invalid_signed = chr(ord(signed[0]) + 1)+signed[1:]

        self.assertNotEqual(signed, invalid_signed)
        with self.assertRaises(InvalidSignedString):
            self.o.data_from_signed(invalid_signed)
        

class QrAESTest(unittest.TestCase):
    CONTENT='HTB00000013401213A0003665574684001201203271120120301201205310001200201205270'

    HEADER = 'https://huistenbosch.tstar.jp'.ljust(40) + '3'

    # QR_DATAの暗号化された文字列はsetUPのcustom_keyで暗号化されたもの
    QR_DATA = HEADER + 'obfWHL4rkQB009ZU3OTaGi2-aZHNY8FfmsVPtRgjGLdARQDRW31pZDiuAXVXaIGv1vjUZxo81n8OK6QEfyVuOwYRq0RTLtXpJkQ2ciRVoLXW9OS28VmlD1TFXv91EL9v'
    # QR_DATAの暗号化された文字列はsetUPのcustom_keyで暗号化されて、勝手に変更することで適切ではない文字列を作る
    INVALID_QR_DATA = HEADER + 'obfWHL4rkQB009ZU3OTaGi2-aZHNY8FfmsVPtRgjGLdARQDRW31pZDiuAXVXaIGv1vjUZxo81n8OK6QEfyVuOwYRq0RTLtXpJkQ2ciRVoLXW9OS28VmlD1TFXv91EL9z'

    def setUp(self):
        self.custom_key = "!THIS_KEY_IS_FOR_THE_UNIT_TESTS!"
        self.builder = qr_aes(self.custom_key)

    def test_make_function(self):
        from altair.aes_urlsafe import AESURLSafe
        aes = AESURLSafe(self.custom_key)
        data = {'header': self.HEADER, 'content': self.CONTENT}
        qr_data = self.builder.make(data)
        qr_data = qr_data[len(self.HEADER):]
        self.assertEqual(aes.decrypt(qr_data), self.CONTENT)

    def test_extract_function_success(self):
        test_data = self.builder.extract(self.QR_DATA, self.HEADER)
        header = test_data['header']
        content = test_data['content']
        self.assertEqual(header, self.HEADER)
        self.assertEqual(content, self.CONTENT)

    def test_extract_function_fail(self):
        test_data = self.builder.extract(self.INVALID_QR_DATA, self.HEADER)
        header = test_data['header']
        content = test_data['content']
        self.assertEqual(header, self.HEADER)
        self.assertNotEqual(content, self.CONTENT)

if __name__ == '__main__':
    unittest.main()
