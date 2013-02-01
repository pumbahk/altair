from .models import Promotion
from altaircms.plugins.widget.promotion.models import PromotionWidget

class Finder(object):
    def __init__(self, request):
        self.request = request

    def get_promotion_widget_pages(self):
        
