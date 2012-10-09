# -*- coding: utf-8 -*-

import unittest
from ticketing.qr import qr

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
        from ticketing.qr import InvalidSignedString

        signed = self.o.sign(self.o.make(self.data))
        invalid_signed = chr(ord(signed[0]) + 1)+signed[1:]

        self.assertNotEqual(signed, invalid_signed)
        with self.assertRaises(InvalidSignedString):
            self.o.data_from_signed(invalid_signed)
        
        
if __name__ == '__main__':
    unittest.main()
