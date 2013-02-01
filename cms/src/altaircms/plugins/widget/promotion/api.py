# -*- coding:utf-8 -*-

from zope.interface import provider
import altaircms.helpers as h
from .interfaces import IPromotionManager
import logging
logger = logging.getLogger(__file__)


from altaircms.page.models import Page
from altaircms.widget.models import Widget
from .models import PromotionWidget

def get_promotion_widget_pages(request):
    return Page.query.filter(PromotionWidget.id==Widget.id,Widget.page_id==Page.id)
get_promotion_widget_pages.widget = PromotionWidget

def get_promotion_manager(request):
    return request.registry.getUtility(IPromotionManager)


@provider(IPromotionManager)
class RealPromotionManager(object):
    @classmethod
    def promotion_info(cls, request, promotion_sheet, idx=0, limit=None):
        return promotion_sheet.as_info(request, idx=idx, limit=limit)
    
    @classmethod
    def main_image_info(cls, request):
        try:
            p = request.context.Promotion.query.filter_by(id=request.GET["promotion_unit_id"]).one()
            return {"id": p.id, 
                    "link": h.link.get_link_from_promotion(request, p), 
                    "src": h.asset.to_show_page(request, p.main_image), 
                    "message": p.text}
        except Exception, e:
            logger.exception(e)
            return {}

    @classmethod
    def show_image(cls, image_path, href):
        return '<a href="%s"><img src="%s"/></a>' % (href, image_path)


## mock
from .models import PromotionInfo
@provider(IPromotionManager)
class MockPromotionManager(object):
    @classmethod
    def promotion_info(cls, request):
        thumbnails = ["/static/mock/img/%d.jpg" % i for i in xrange(1, 16)]
        return PromotionInfo(
            thumbnails = thumbnails, 
            idx = 0, 
            message = u"test message", 
            main = "/static/mock/img/1.jpg", 
            main_link = "http://example.com", 
            links = ["#"] * len(thumbnails), 
            messages = [u"ここに何かメッセージ"] * len(thumbnails), 
            interval_time= 5000, 
            unit_candidates = range(1, 16)
            )

    @classmethod
    def main_image_info(cls, request):
        i = request.GET["promotion_unit_id"]
        import random
        return {"id": 1, 
                "link": "http://google.co.jp", 
                "src": "/static/mock/img/%s.jpg" % i, 
                "message": u"this message from api %f" % random.random()}

    @classmethod
    def show_image(cls, image_path, href):
        return '<a href="%s"><img src="%s"/></a>' % (href, image_path)
