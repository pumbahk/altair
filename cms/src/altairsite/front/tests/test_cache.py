# -*- coding:utf-8 -*-
import mock
import unittest
from pyramid import testing
from pyramid.response import Response

def make_smartphone_request(request):
    from altair.mobile.interfaces import ISmartphoneRequest
    from zope.interface import directlyProvides
    directlyProvides(request, ISmartphoneRequest)
    return request

def make_mobile_request(request):
    from altair.mobile.interfaces import IMobileRequest
    from zope.interface import directlyProvides
    directlyProvides(request, IMobileRequest)
    return request


class LookupTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altairsite.front.install_page_key_generator")

    def _callFUT(self, request):
        from ..cache import get_key_generator
        return get_key_generator(request)

    def test_pc_request(self):
        request = testing.DummyRequest()
        result = self._callFUT(request)
        self.assertEquals(result.prefix, "P:")

    def test_mobile_request(self):
        request = make_mobile_request(testing.DummyRequest())
        result = self._callFUT(request)
        self.assertEquals(result.prefix, "M:")

    def test_smartphone_request(self):
        request = make_smartphone_request(testing.DummyRequest())
        result = self._callFUT(request)
        self.assertEquals(result.prefix, "S:")
        

class Tests(unittest.TestCase):
    def setup_fixture(self, config):
        from altair.mobile.interfaces import ISmartphoneRequest
        from altair.mobile.interfaces import IMobileRequest
        from pyramid.interfaces import IRequest
        from ..cache import (
            ICacheKeyGenerator, 
            IFrontPageCache, 
            CacheKeyGenerator, 
            OnMemoryCacheStore, 
            WrappedFrontPageCache, 
            update_browser_id
        )
        config.registry.adapters.register([ISmartphoneRequest], ICacheKeyGenerator, "", CacheKeyGenerator("S:"))
        config.registry.adapters.register([IMobileRequest], ICacheKeyGenerator, "", CacheKeyGenerator("M:"))
        config.registry.adapters.register([IRequest], ICacheKeyGenerator, "", CacheKeyGenerator("P:"))
        self.cache = front_page_cache = WrappedFrontPageCache(OnMemoryCacheStore(), update_browser_id)
        config.registry.registerUtility(front_page_cache, IFrontPageCache)

    def get_reponse_body(self):
        return u"""
*result*
<img src="//rt.example.jp/-/bi/189528fa00e0c11bd46770e2dc23f41f2dddf4ab.gif" width="0" height="0" />
"""

    def setUp(self):
        self.config = testing.setUp(settings={
            "altaircms.tracking.image.impl" : "altairsite.tracking.TrackingImageTagGenerator", 
            "altaircms.tracking.image.urlprefix": "//rt.example.jp/-/bi/"

        })
        self.config.include("altairsite.install_tracking_image_generator")
        self.setup_fixture(self.config)

    def _getTarget(self):
        from altairsite.front.cache import cached_view_tween
        return cached_view_tween

    def test_first_request(self):
        response_body = self.get_reponse_body()
        def view(request):
            return Response(response_body)

        target = self._getTarget()
        fn = target(view, self.config.registry)
        request = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
        result = fn(request)
        self.assertEquals(result.text, response_body)

        ## cached
        self.assertEquals(self.cache.cache.cache, {'P:http://rt.example.jp/foo/bar?foo=1': {'content_type':'text/html', 'charset': 'UTF-8', 'body':response_body}})

    def test_not_cache__when_not_text_response(self):
        def view(request):
            response = Response("*")
            response.content_type = "image/jpeg" #not text/* or application/json
            return response

        target = self._getTarget()
        fn = target(view, self.config.registry)
        request = testing.DummyRequest(url="http://rt.example.jp/static/image.jpg")

        result = fn(request)
        self.assertEquals(result.text, "*")

        ## not cache
        self.assertEquals(self.cache.cache.cache, {})
        
    def test_it(self):
        response_body = self.get_reponse_body()
        def view(request):
            return Response(response_body)

        ## first
        target = self._getTarget()
        fn = target(view, self.config.registry)
        request = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
        result = fn(request)
        self.assertEquals(result.text, response_body)

        ## second(cached)
        request2 = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
        request2.headers["X-Altair-Browserid"] = "*replaced*"
        result = fn(request2)
        self.assertEquals(result.text,  u"""
*result*
<img src="//rt.example.jp/-/bi/*replaced*.gif" width="0" height="0" />
""")

    def test_preview_request__not_cached(self):
        response_body = self.get_reponse_body()
        def view(request):
            return Response(response_body)

        ## first
        target = self._getTarget()
        fn = target(view, self.config.registry)
        request = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
        result = fn(request)
        self.assertEquals(result.text, response_body)

        ## second(cached)
        with mock.patch("altairsite.front.cache.get_key_generator", autospec=True) as get_key_generator:
            get_key_generator.side_effect = NotImplementedError("don't call")

            from altair.preview.api import set_preview_request_condition
            request2 = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
            request2.headers["X-Altair-Browserid"] = "*replaced*"
            set_preview_request_condition(request2, True)
            result = fn(request2)

            self.assertEquals(result.text, response_body)
            self.assertFalse(get_key_generator.called)
