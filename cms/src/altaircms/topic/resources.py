from pyramid.decorator import reify

from ..widget.api import get_has_widget_pages_finder
from ..security import get_acl_candidates
from ..tag.api import get_tagmanager

from .searcher import TopicPageListSearcher
from .searcher import TopcontentPageListSearcher
from .searcher import PromotionPageListSearcher
from .searcher import TopicPageDetailSearcher
from .searcher import TopcontentPageDetailSearcher
from .searcher import PromotionPageDetailSearcher
from altaircms.topic.models import Topic
from altaircms.topic.models import Topcontent
from altaircms.topic.models import Promotion

from .viewhelpers import TopicGrid
from .viewhelpers import TopicHTMLRenderer
from .viewhelpers import TopcontentGrid
from .viewhelpers import TopcontentHTMLRenderer
from .viewhelpers import PromotionGrid
from .viewhelpers import PromotionHTMLRenderer

class TopicPageContext(object):
    def __init__(self, request):
        self.request = request
    widgettype = "topic"

    Grid = TopicGrid
    TargetTopic = Topic
    HTMLRenderer = TopicHTMLRenderer

    @property
    def __acl__(self):
        return get_acl_candidates()

    @reify
    def finder(self):
        return get_has_widget_pages_finder(self.request, self.widgettype)

    @reify
    def tag_manager(self):
        return get_tagmanager(self.widgettype, request=self.request)

    @reify
    def list_searcher(self):
        return TopicPageListSearcher(self.request, self.finder)

    @reify
    def detail_searcher(self):
        return TopicPageDetailSearcher(self.request, self.finder)

class TopcontentPageContext(object):
    def __init__(self, request):
        self.request = request
    widgettype = "topcontent"

    Grid = TopcontentGrid
    TargetTopic = Topcontent
    HTMLRenderer = TopcontentHTMLRenderer

    @property
    def __acl__(self):
        return get_acl_candidates()

    @reify
    def finder(self):
        return get_has_widget_pages_finder(self.request, self.widgettype)

    @reify
    def tag_manager(self):
        return get_tagmanager(self.widgettype, request=self.request)
    @reify
    def list_searcher(self):
        return TopcontentPageListSearcher(self.request, self.finder)

    @reify
    def detail_searcher(self):
        return TopcontentPageDetailSearcher(self.request, self.finder)

class PromotionPageContext(object):
    def __init__(self, request):
        self.request = request
    widgettype = "promotion"

    Grid = PromotionGrid
    TargetTopic = Promotion
    HTMLRenderer = PromotionHTMLRenderer

    @property
    def __acl__(self):
        return get_acl_candidates()

    @reify
    def finder(self):
        return get_has_widget_pages_finder(self.request, self.widgettype)

    @reify
    def tag_manager(self):
        return get_tagmanager(self.widgettype, request=self.request)

    @reify
    def list_searcher(self):
        return PromotionPageListSearcher(self.request, self.finder)

    @reify
    def detail_searcher(self):
        return PromotionPageDetailSearcher(self.request, self.finder)

class TopicTagContext(object):
    classifier = "topic"
    def __init__(self, request):
        self.request = request

class TopcontentTagContext(object):
    classifier = "topcontent"
    def __init__(self, request):
        self.request = request

class PromotionTagContext(object):
    classifier = "promotion"
    def __init__(self, request):
        self.request = request
