# -*- coding:utf-8 -*-

import unittest
from webob import Request

class raw_cookiesTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import raw_cookies
        return raw_cookies(*args, **kwargs)

    def test_empty(self):
        request = Request.blank('http://example.com')
        result = self._callFUT(request)

        self.assertEqual(result, {})

    def test_it(self):
        request = Request.blank('http://example.com')
        request.headers['Cookie'] = 'test=value'
        result = self._callFUT(request)

        self.assertEqual(result, {'test': 'value'})

    def test_utf8(self):
        request = Request.blank('http://example.com')
        request.cookies['testing'] = b'あああああああ'
        result = self._callFUT(request)

        self.assertEqual(result, {'testing': b'あああああああ'})

    def test_sjis(self):
        request = Request.blank('http://example.com')
        request.headers['Cookie'] = u'test="あああああ"'.encode('sjis')
        result = self._callFUT(request)

        self.assertEqual(result, {'test': u'あああああ'.encode('sjis')})

