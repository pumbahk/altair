import unittest
from pyramid import testing
from altaircms.models import DBSession, Base
from altaircms import helpers as h

def withDB(o, flush=False):
    DBSession.add(o)
    if flush:
        DBSession.flush()
    return o

def makePageset(*args, **kwargs):
    from altaircms.page.models import PageSet
    return PageSet(*args, **kwargs)

def makePromotionUnit(*args, **kwargs):
    from altaircms.plugins.widget.promotion.models import PromotionUnit
    return PromotionUnit(*args, **kwargs)

def makePromotion(*args, **kwargs):
    from altaircms.plugins.widget.promotion.models import Promotion
    return Promotion(*args, **kwargs)

def makeImageasset(*args, **kwargs):
    from altaircms.asset.models import ImageAsset
    return ImageAsset(*args, **kwargs)

class PromotionUnitTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altairsite.front")

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _makeOne(self, *args, **kwargs):
        from altaircms.plugins.widget.promotion.models import PromotionUnit
        return PromotionUnit(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        return target.get_link(*args, **kwargs)

    def test_it_with_url(self):
        target = self._makeOne(text=u"text", link=u"http://www.google.co.jp")

        request = testing.DummyRequest()
        result = self._callFUT(target, request)
        
        self.assertEquals("http://www.google.co.jp", result)

    def test_it_with_pageset_pu(self):
        pageset = makePageset(url=u"foo/bar")
        target = self._makeOne(text=u"text", pageset=pageset)

        request = testing.DummyRequest()
        result = self._callFUT(target, request)

        self.assertEquals(result, h.link.unquote_path_segment(request.route_path("front", page_name=pageset.url)))


class PromotionManagerTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include("altairsite.front")
        self.config.include("altaircms.asset")

    def tearDown(self):
        import transaction
        transaction.abort()
        testing.tearDown()

    def _getTarget(self, *args, **kwargs):
        from altaircms.plugins.widget.promotion.api import RealPromotionManager
        return RealPromotionManager

    def test_promotion_info(self):
        main_image = makeImageasset(id=1)
        thumbnail = makeImageasset(id=2)
        pu = makePromotionUnit(text=u"text", link=u"http://www.google.co.jp", 
                               id=1, main_image=main_image, thumbnail=thumbnail)
        promotion = makePromotion(promotion_units=[pu])
        result = self._getTarget().promotion_info(testing.DummyRequest(), promotion)

        self.assertEquals(result.message, u"text")
        self.assertNotEquals(result.main, None) ##
        self.assertNotEquals(result.thumbnails, []) ##
        self.assertEquals(result.main_link, "http://www.google.co.jp")
        self.assertEquals(result.links, ["http://www.google.co.jp"])

    def test_main_image_info(self):
        main_image = makeImageasset()
        thumbnail = makeImageasset()
        pu = makePromotionUnit(text=u"text", link=u"http://www.google.co.jp", 
                               main_image=main_image, thumbnail=thumbnail)
        
        promotion = withDB(makePromotion(promotion_units=[pu]), flush=True)
        request = testing.DummyRequest(GET=dict(promotion_unit_id=promotion.id))
        from altaircms.plugins.widget.promotion.models import PromotionWidgetResource
        request.context =  PromotionWidgetResource(request)
        result = self._getTarget().main_image_info(request)

        self.assertEquals(u"text", result["message"])
        self.assertEquals(u'http://www.google.co.jp', result["link"])

if __name__ == "__main__":
    unittest.main()
