# -*- coding:utf-8 -*-
import unittest
import datetime

class PythonNWTSUploaderTest(unittest.TestCase):
    def setUp(self):
        def sej_dummy_response(environ):
            return ''
        from .webapi import DummyServer
        self.dummy_server = DummyServer(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        self.dummy_server.start()

    def tearDown(self):
        self.dummy_server.stop()

    def _getTarget(self):
        from ..nwts import PythonNWTSUploader
        return PythonNWTSUploader

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_nwts_template(self):
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(
            endpoint_url='http://localhost:48080/',
            terminal_id='60022000',
            password='60022a'
            )
        target('test.asp', 'SEIT020U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.body, "6002200060022aSEIT020U\x0a\0\0\0\0\0\0\0" "1234567890")

        self.assertEqual(self.dummy_server.request.content_type, 'text/plain')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertRegexpMatches(self.dummy_server.request.url, r'^http://localhost:48080/test.asp\?Mode=1&ThreadID=\d+')

    def test_nwts_refund(self):
        '''
        NWTS Refund upload
        '''
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(
            endpoint_url='http://localhost:48080/',
            terminal_id='60022000',
            password='60022a'
            )
        target('test.asp', 'SDMT010U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.body, "6002200060022aSDMT010U\x0a\0\0\0\0\0\0\0" "1234567890")
        self.assertEqual(self.dummy_server.request.content_type, 'text/plain')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertRegexpMatches(self.dummy_server.request.url, r'http://localhost:48080/test.asp\?Mode=2&ThreadID=\d+')


class ProxyNWTSUploaderTest(unittest.TestCase):
    def setUp(self):
        def sej_dummy_response(environ):
            return ''
        from .webapi import DummyServer
        self.dummy_server = DummyServer(sej_dummy_response, host='127.0.0.1', port=48080, status=200)
        self.dummy_server.start()

    def tearDown(self):
        self.dummy_server.stop()

    def _getTarget(self):
        from ..nwts import ProxyNWTSUploader
        return ProxyNWTSUploader

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_nwts_template(self):
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(
            proxy_url='http://localhost:48080/',
            proxy_auth_user='user',
            proxy_auth_password='password',
            endpoint_url='http://www.example.com/sdmt',
            terminal_id='60022000',
            password='60022a'
            )
        target('test.asp', 'SEIT020U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.content_type, 'multipart/form-data')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertEqual(self.dummy_server.request.POST['-s'], 'www.example.com')
        self.assertEqual(self.dummy_server.request.POST['-d'], '/sdmt')
        self.assertEqual(self.dummy_server.request.POST['-t'], '60022000')
        self.assertEqual(self.dummy_server.request.POST['-p'], '60022a')
        self.assertEqual(self.dummy_server.request.POST['-e'], 'test.asp')
        self.assertEqual(self.dummy_server.request.POST['-f'], 'SEIT020U')
        self.assertEqual(self.dummy_server.request.POST['zipfile'], '1234567890')


    def test_nwts_refund(self):
        '''
        NWTS Refund upload
        '''
        '''
        NWTS Template upload
        '''
        import webob.util

        webob.util.status_reasons[800] = 'OK'

        target = self._makeOne(
            proxy_url='http://localhost:48080/',
            proxy_auth_user='user',
            proxy_auth_password='password',
            endpoint_url='http://www.example.com/sdmt',
            terminal_id='60022000',
            password='60022a'
            )
        target('test.asp', 'SDMT010U', '1234567890')

        self.dummy_server.poll()

        self.assertEqual(self.dummy_server.request.content_type, 'multipart/form-data')
        self.assertEqual(self.dummy_server.request.method, 'POST')
        self.assertEqual(self.dummy_server.request.POST['-s'], 'www.example.com')
        self.assertEqual(self.dummy_server.request.POST['-d'], '/sdmt')
        self.assertEqual(self.dummy_server.request.POST['-t'], '60022000')
        self.assertEqual(self.dummy_server.request.POST['-p'], '60022a')
        self.assertEqual(self.dummy_server.request.POST['-e'], 'test.asp')
        self.assertEqual(self.dummy_server.request.POST['-f'], 'SDMT010U')
        self.assertEqual(self.dummy_server.request.POST['zipfile'], '1234567890')

if __name__ == u"__main__":
    import os
    print os.getpid()
    unittest.main()


