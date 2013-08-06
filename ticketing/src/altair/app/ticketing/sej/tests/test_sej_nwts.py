# -*- coding:utf-8 -*-
import unittest
import datetime

from altair.app.ticketing.sej.nwts import nws_data_send

class SejTestNwts(unittest.TestCase):
    def setUp(self):
        def sej_dummy_response(environ):
            return ''
        from .webapi import DummyServer
        self.dummy_server = DummyServer(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        self.dummy_server.start()

    def tearDown(self):
        self.dummy_server.stop()

    def test_nwts_template(self):
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        nws_data_send('http://localhost:48080/', '60022000', '60022a', 'SEIT020U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.body, "6002200060022aSEIT020U\x0a\0\0\0\0\0\0\0" "1234567890")

        self.assertEqual(self.dummy_server.request.content_type, 'text/plain')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertRegexpMatches(self.dummy_server.request.url, r'^http://localhost:48080/\?Mode=1&ThreadID=\d+')

    def test_nwts_refund(self):
        '''
        NWTS Refund upload
        '''
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        nws_data_send('http://localhost:48080/', '60022000', '60022a', 'SDMT010U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.body, "6002200060022aSDMT010U\x0a\0\0\0\0\0\0\0" "1234567890")
        self.assertEqual(self.dummy_server.request.content_type, 'text/plain')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertRegexpMatches(self.dummy_server.request.url, r'http://localhost:48080/\?Mode=2&ThreadID=\d+')


if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()


