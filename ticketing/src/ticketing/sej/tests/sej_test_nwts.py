# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.nwts import nws_data_send

class SejTestNwts(unittest.TestCase):

    def _getTarget(self):
        import webapi
        return webapi.DummyServer

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_nwts_template(self):
        '''
        NWTS Template upload
        '''
        import webob.util

        def sej_dummy_response(environ):
            return ''

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        target.start()

        nws_data_send('http://localhost:48080/', '60022000', '60022a', 'SEIT020U', '1234567890')

        target.assert_body("6002200060022aSEIT020U\x0a\0\0\0\0\0\0\0" + "1234567890")

        target.assert_content_type('text/plain')
        target.assert_method('POST')
        target.assert_url('http://localhost:48080/?Mode=1&ThreadID=9')

    def test_nwts_refund(self):
        '''
        NWTS Refund upload
        '''
        '''
        NWTS Template upload
        '''
        import webob.util

        def sej_dummy_response(environ):
            return ''

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=48081, status=200)
        target.start()

        nws_data_send('http://localhost:48081/', '60022000', '60022a', 'SDMT010U', '1234567890')

        target.assert_body("6002200060022aSDMT010U\x0a\0\0\0\0\0\0\0" + "1234567890")
        target.assert_content_type('text/plain')
        target.assert_method('POST')
        target.assert_url('http://localhost:48081/?Mode=2&ThreadID=9')


if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()


