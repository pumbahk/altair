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

    def test_nwts(self):
        import webob.util

        def sej_dummy_response(environ):
            return ''

        webob.util.status_reasons[800] = 'OK'
        target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        target.start()

        nws_data_send('http://localhost:48080/', '60022000', '60022a', 'SEIT020U', '1234567890')

        assert target.request.body == "6002200060022aSE" + \
                                      "IT020U\x0a\x00\x00\x00\x00\x00\x00\x00\x00\x00" +\
                                      "\x00\x00\x00\x001234567890"


        nws_data_send('http://sv2.ticketstar.jp/test.php', '60022000', '60022a', 'SEIT020U', '1234567890')

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()


