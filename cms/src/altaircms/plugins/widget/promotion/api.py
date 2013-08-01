# -*- coding:utf-8 -*-

from sqlalchemy.orm.exc import NoResultFound
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

_INTERVAL_TIME = 5000
def set_interval_time(n):
    global _INTERVAL_TIME
    logger.info("*promotion widget interval time: %s -> %s" % (_INTERVAL_TIME, n))
    _INTERVAL_TIME = n

def get_interval_time():
    global _INTERVAL_TIME
    return _INTERVAL_TIME

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
                    "src": h.asset.rendering_object(request, p.main_image).filepath, 
                    "width": p.main_image.width, 
                    "height": p.main_image.height, 
                    "message": p.text}
        except NoResultFound:
            return {}
        except Exception, e:
            logger.exception(e)
            return {}

    @classmethod
    def show_image(cls, i, image_path, href):
        return '<a href="%s"><img id="promotion%s" src="%s"/></a>' % (href, i, image_path)


## mock
from .utilities import PromotionInfo
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
                "width": 300, 
                "height": 300, 
                "message": u"this message from api %f" % random.random()}

    @classmethod
    def show_image(cls, image_path, href):
        return '<a href="%s"><img src="%s"/></a>' % (href, image_path)
