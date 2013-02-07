from pyramid.decorator import reify

from ..widget.api import get_has_widget_pages_finder
from ..security import get_acl_candidates
from .searcher import TopcontentPageListSearcher
from .searcher import PromotionPageListSearcher

class TopcontentPageContext(object):
    def __init__(self, request):
        self.request = request
    widgettype = "topcontent"

    @property
    def __acl__(self):
        return get_acl_candidates()

    @reify
    def finder(self):
        return get_has_widget_pages_finder(self.request, self.widgettype)

    @reify
    def searcher(self):
        return TopcontentPageListSearcher(self.request, self.finder)

class PromotionPageContext(object):
    def __init__(self, request):
        self.request = request
    widgettype = "promotion"

    @property
    def __acl__(self):
        return get_acl_candidates()

    @reify
    def finder(self):
        return get_has_widget_pages_finder(self.request, self.widgettype)

    @reify
    def searcher(self):
        return PromotionPageListSearcher(self.request, self.finder)

class TopcontentTagContext(object):
    classifier = "topcontent"
    def __init__(self, request):
        self.request = request
class PromotionTagContext(object):
    classifier = "promotion"
    def __init__(self, request):
        self.request = request
    
    
