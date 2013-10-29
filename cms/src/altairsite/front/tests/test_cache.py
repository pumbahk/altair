# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from pyramid.response import Response

class Tests(unittest.TestCase):
    def setup_fixture(self, config):
        from altair.mobile.interfaces import ISmartphoneRequest
        from altair.mobile.interfaces import IMobileRequest
        from pyramid.interfaces import IRequest
        from ..cache import (
            ICacheKeyGenerator, 
            IFrontPageCache, 
            CacheKeyGenerator, 
            OnMemoryFrontPageCacher, 
            WrappedFrontPageCache, 
            update_browser_id
        )
        config.registry.adapters.register([ISmartphoneRequest], ICacheKeyGenerator, "", CacheKeyGenerator("S:"))
        config.registry.adapters.register([IMobileRequest], ICacheKeyGenerator, "", CacheKeyGenerator("M:"))
        config.registry.adapters.register([IRequest], ICacheKeyGenerator, "", CacheKeyGenerator("P:"))
        front_page_cache = WrappedFrontPageCache(OnMemoryFrontPageCacher(), update_browser_id)
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

    def test_no_cache(self):
        response_body = self.get_reponse_body()
        def view(request):
            return Response(response_body)

        target = self._getTarget()
        fn = target(view, self.config.registry)
        request = testing.DummyRequest(url="http://rt.example.jp/foo/bar?foo=1")
        result = fn(request)
        self.assertEquals(result.text, response_body)

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
