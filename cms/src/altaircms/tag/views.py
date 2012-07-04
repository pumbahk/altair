from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.lib.fanstatic_decorator import with_bootstrap
from altaircms.tag.api import get_tagmanager
from .manager import QueryParser
from . import SUPPORTED_CLASSIFIER
from . import forms


def in_support_classifier(context, request):
    return request.matchdict.get("classifier") in SUPPORTED_CLASSIFIER

def has_query(context, request):
    return "query" in request.GET

@view_defaults(route_name="tag", decorator=with_bootstrap, permission="tag_read")
class TopView(object):
    RECENT_CHANGE_TAGS_LIMIT = 5
    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET", renderer="altaircms:templates/tag/top.mako")
    def toppage_view_default(self):
        form = forms.TagSearchForm()
        pages = get_tagmanager("page").recent_change_tags()
        assets = get_tagmanager("asset").recent_change_tags()
        new_tags_dict = dict(
            page=self.request.allowable("PageTag", qs=pages).limit(self.RECENT_CHANGE_TAGS_LIMIT), 
            asset=self.request.allowable("AssetTag", qs=assets).limit(self.RECENT_CHANGE_TAGS_LIMIT)
            )
        return {"supported": SUPPORTED_CLASSIFIER, "form": form, 
                "new_tags_dict": new_tags_dict}

    @view_config(request_method="GET",custom_predicates=(has_query, ), 
                 renderer="altaircms:templates/tag/search_result.mako")
    def search(self):
        form = forms.TagSearchForm(**self.request.GET)
        classifier = self.request.GET["classifier"]
        query = self.request.GET["query"]
        manager = get_tagmanager(classifier)
        query_result = QueryParser(query).and_search_by_manager(manager)
        query_result = self.request.allowable(manager.Object.__name__, qs=query_result)
        return {"supported": SUPPORTED_CLASSIFIER, 
                "form": form, 
                "query_result": query_result, 
                "classifier":classifier}

    @view_config(request_method="GET", custom_predicates=(in_support_classifier, ), 
                 renderer="altaircms:templates/tag/subtop.mako")
    def subtoppage_view(self):
        classifier = self.request.matchdict["classifier"]
        form = forms.TagSearchForm(classifier=classifier)
        manager = get_tagmanager(classifier)
        tags = self.request.allowable(manager.Object.__name__, qs=manager.recent_change_tags())
        new_tags = tags.limit(self.RECENT_CHANGE_TAGS_LIMIT)
        return {"classifier": classifier, 
                "new_tags": new_tags, 
                "tags": tags, 
                "form": form, 
                "supported": SUPPORTED_CLASSIFIER}
