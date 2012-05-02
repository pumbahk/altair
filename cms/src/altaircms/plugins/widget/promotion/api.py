from zope.interface import directlyProvides

from .interfaces import IPromotionManager

def get_promotion_manager(request):
    return request.registry.getUtility(IPromotionManager)

class RealPromotionManager(object):
    @classmethod
    def promotion_info(cls, request):
        promotion = request.context.Promotion.filter(id=request.GET["promotion_id"])
        return promotion.as_info(idx=request.GET["promotion_idx"], limit=request.GET.get("limit", None))
    
    @classmethod
    def main_image_info(cls, request):
        punit = request.context.PromotionUnit.filter_by(id=request.GET["promotion_unit_id"])
        return {"id": punit.id, 
                "main_image_id": punit.main_image.id, 
                "main_message": punit.text}
directlyProvides(RealPromotionManager, IPromotionManager)

## mock
from .models import PromotionInfo
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

directlyProvides(MockPromotionManager, IPromotionManager)
