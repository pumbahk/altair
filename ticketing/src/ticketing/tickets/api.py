from ticketing.core import models as cmodels

class AttributeAggregator(object):
    def __init__(self, request):
        self.requset = request

    def build(self, ordered_product_item):
        
