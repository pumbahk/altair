from altaircms.tag.forms import PublicTagForm
class PromotionTagContext(object):
    classifier = "promotion"
    def __init__(self, request):
        self.request = request
    
    
