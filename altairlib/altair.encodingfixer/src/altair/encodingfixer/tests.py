# -*- coding:utf-8 -*-

import unittest
from pyramid import testing

class EncodingFixerTweenTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from . import EncodingFixerTween
        return EncodingFixerTween

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)
        

    def test_it(self):
        reg = self.config.registry
        dummy_hanlder = lambda request: request.response
        target = self._makeOne(dummy_hanlder, reg)

        request = testing.DummyRequest()
        result = target(request)

        self.assertEqual(result, request.response)


    def test_invalid_path_info(self):
        reg = self.config.registry
        dummy_hanlder = lambda request: request.path
        target = self._makeOne(dummy_hanlder, reg)

        from pyramid.request import Request

        env = {
            'PATH_INFO': (u'あああああ').encode('Shift_JIS'),
            }
        request = Request(env)
        request.response = object()

        result = target(request)

        self.assertEqual(result.status_int, 400)

    def test_invalid_query_string(self):
        reg = self.config.registry
        dummy_hanlder = lambda request: request.path
        target = self._makeOne(dummy_hanlder, reg)

        from pyramid.request import Request
        import urllib

        env = {
            'PATH_INFO': '',
            'QUERY_STRING': urllib.urlencode({u'あああ'.encode('Shift_JIS'): u'いいい'.encode('Shift_JIS')})
            }

        request = Request(env)
        request.response = object()

        result = target(request)

        self.assertEqual(result.status_int, 400)
