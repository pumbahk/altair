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
    from collections import OrderedDict

    item_list_1 = OrderedDict([
        ('id_code', 10),
        ('type_code', 1),
        ('ticket_code', 6),
        ('serial_no', 17),
        ('issued_at', 8),
        ('count_flag', 1),
        ('season_flag', 1),
        ('valid_date_from', 8),
        ('valid_date_to', 8),
        ('enterable_days', 3),
        ('enterable_from', 4),
        ('usable_date_to', 8),
        ('special_flag', 1)
    ])

    item_list_2 = OrderedDict([
        ('id_code', 10),
        ('type_code', 1),
        ('ticket_code', 6),
        ('serial_no', 17),
        ('issued_at', 8),
        ('count_flag', 1),
        ('season_flag', 1),
        ('valid_date_to', 8),
        ('enterable_days', 3),
        ('enterable_from', 4),
        ('usable_date_to', 8),
        ('special_flag', 1)
    ])

    item_list_3 = {
        'id_code': 10,
        'type_code': 1,
        'ticket_code': 6,
        'serial_no': 17,
        'issued_at': 8,
        'count_flag': 1,
        'season_flag': 1,
        'valid_date_from': 8,
        'valid_date_to': 8,
        'enterable_days': 3,
        'enterable_from': 4,
        'usable_date_to': 8,
        'special_flag': 1
    }

    valid_data = {
        'id_code': 'HTB0000001',
        'type_code': '3',
        'ticket_code': '401213',
        'serial_no': 'A0003665574684001',
        'issued_at': '20120327',
        'count_flag': '1',
        'season_flag': '1',
        'valid_date_from': '20120301',
        'valid_date_to': '20120531',
        'enterable_days': '000',
        'enterable_from': '1200',
        'usable_date_to': '20120527',
        'special_flag': '0'
    }

    CONTENT='HTB00000013401213A0003665574684001201203271120120301201205310001200201205270'

    HEADER = 'http://www.shop-huistenbosch.jp/3'

    QR_DATA = 'http://www.shop-huistenbosch.jp/3nYyHHNKDT0-Cq2jKGvb2GK_bKVTCknjugFQQpm2a0MUkg-pH8d3ZFSx2lVryOmEkCd7bcZsQuzbZKcM1IMCE6zsfE1skMQrtTYbQiB9Jx8ZxBRAUGr8bdc6vVAnmxZm8'

    def setUp(self):
        self.builder = qr_aes()

    def test_make_function(self):
        from altair.aes_urlsafe import AESURLSafe
        aes = AESURLSafe()
        data = {'header': self.HEADER, 'content': self.CONTENT}
        qr_data = self.builder.make(data)
        qr_data = qr_data[len(self.HEADER):]

        self.assertEqual(aes.decrypt(qr_data), self.CONTENT)

    def test_extract_function_success(self):
        test_data = self.builder.extract(self.QR_DATA, self.HEADER, self.item_list_1)
        self.assertDictEqual(test_data, self.valid_data)


    def test_extract_function_fail_caused_by_no_data_input(self):
        with self.assertRaises(InvalidItemList):
            self.builder.extract(self.QR_DATA, self.HEADER, None)

    def test_extract_function_fail_caused_by_wrong_item_list(self):
        with self.assertRaises(InvalidItemList):
            self.builder.extract(self.QR_DATA, self.HEADER, self.item_list_2)

    def test_extract_function_fail_caused_by_non_order_item_list(self):
        with self.assertRaises(InvalidItemList):
            self.builder.extract(self.QR_DATA, self.HEADER, self.item_list_3)

if __name__ == '__main__':
    unittest.main()
