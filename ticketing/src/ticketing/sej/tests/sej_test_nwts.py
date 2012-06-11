# -*- coding:utf-8 -*-
import unittest
import datetime

from ticketing.sej.nwts import exec_nwts

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

        #webob.util.status_reasons[800] = 'OK'
        #target = self._makeOne(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        #target.start()

        #
        #def exec_nwts(server_host, dir_name, terminal_id, password, file_id, file_name, path):
        exec_nwts('incp.r1test.com', '/cpweb/master/ul', '160022000', '60022a', 'SEIT020U', './data/test', 'tpayback.asp')

        #print target.request.body

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()


