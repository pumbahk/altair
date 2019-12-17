# -*- coding:utf-8 -*-

import logging
from pyramid.compat import escape
logger  = logging.getLogger(__name__)

from pyramid.view import view_config
from pyramid.view import view_defaults
from altaircms.auth.models import Organization
from altaircms.helpers.viewhelpers import FlashMessage
from altaircms.lib.fanstatic_decorator import with_bootstrap
from .api import get_tagmanager, tags_from_string, notify_created_tags, string_from_tags
from .manager import QueryParser
from . import SUPPORTED_CLASSIFIER
from . import forms
from .models import PageTag
from .models import AssetTag
from altaircms.models import DBSession


def in_support_classifier(context, request):
    return request.matchdict.get("classifier") in SUPPORTED_CLASSIFIER

def has_query(context, request):
    return "query" in request.GET

@view_defaults(route_name="tag", decorator=with_bootstrap, permission="tag_read")
class TopView(object):
    RECENT_CHANGE_TAGS_LIMIT = 5
    def __init__(self, request):
        self.request = request

    @view_config(request_method="GET", renderer="altaircms:templates/tag/top.html")
    def toppage_view_default(self):
        form = forms.TagSearchForm()
        pages = get_tagmanager("page", self.request).recent_change_tags()
        assets = get_tagmanager("asset", self.request).recent_change_tags()
        new_tags_dict = dict(
            page=self.request.allowable(PageTag, qs=pages).limit(self.RECENT_CHANGE_TAGS_LIMIT), 
            asset=self.request.allowable(AssetTag, qs=assets).limit(self.RECENT_CHANGE_TAGS_LIMIT)
            )
        return {"supported": SUPPORTED_CLASSIFIER, "form": form, 
                "new_tags_dict": new_tags_dict}

    @view_config(request_method="GET",custom_predicates=(has_query, ), 
                 renderer="altaircms:templates/tag/search_result.html")
    def search(self):
        form = forms.TagSearchForm(**self.request.GET)
        classifier = self.request.GET["classifier"]
        query = self.request.GET["query"]
        manager = get_tagmanager(classifier, self.request)
        query_result = QueryParser(query).and_search_by_manager(manager, self.request.organization.id)
        query_result = self.request.allowable(manager.Object.__name__, qs=query_result)
        return {"supported": SUPPORTED_CLASSIFIER, 
                "form": form, 
                "query_result": query_result, 
                "classifier":classifier}

    @view_config(request_method="GET", custom_predicates=(in_support_classifier, ), 
                 renderer="altaircms:templates/tag/subtop.html")
    def subtoppage_view(self):
        classifier = self.request.matchdict["classifier"]
        form = forms.TagSearchForm(classifier=classifier)
        manager = get_tagmanager(classifier, self.request)
        tags = self.request.allowable(manager.Object.__name__, qs=manager.recent_change_tags())
        new_tags = tags.limit(self.RECENT_CHANGE_TAGS_LIMIT)
        return {"classifier": classifier, 
                "new_tags": new_tags, 
                "tags": tags, 
                "form": form, 
                "supported": SUPPORTED_CLASSIFIER}

class BaseTagCreateView(object):
    tag_form_classs = forms.TagForm
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def input(self):
        form = self.tag_form_class()
        return {"form": form}

    def create(self):
        try:
            form = self.tag_form_class(self.request.POST)
            if not form.validate():
                return {"status": False}

            classifier = self.context.classifier
            manager = get_tagmanager(classifier, request=self.request)

            labels = tags_from_string(form.data["tags"])
            encode_labesls = [escape(label) for label in labels]
            tags = manager.get_or_create_tag_list(encode_labesls, public_status=form.data["public_status"])
            for tag in tags:
                DBSession.add(tag)
            notify_created_tags(self.request, tags)
            return {"status": True, "data": {"tags": encode_labesls},
                    "message": u"「%s」が追加されました" % string_from_tags(tags)}
        except Exception, e:
            logger.exception(str(e))

class PublicTagCreateView(BaseTagCreateView):
    tag_form_class = forms.PublicTagForm
class PrivateTagCreateView(BaseTagCreateView):
    tag_form_class = forms.PrivateTagForm

class TagDeleteView(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def delete(self):
        try:
            form = self.tag_form_class(self.request.POST)
            if not form.validate():
                return {"status": False}

            classifier = self.context.classifier
            manager = get_tagmanager(classifier, request=self.request)

            labels = tags_from_string(form.data["tags"])        
            public_status = form.data["public_status"]
            expect_deleted = []

            for label in labels:
                num_of_bound = manager.search_by_tag_label(label).filter(manager.Tag.publicp==public_status).count()
                if num_of_bound <= 0:
                    expect_deleted.append(label)

            qs = manager.Tag.query.filter_by(publicp=public_status).filter(manager.Tag.label_in(expect_deleted))
            qs.delete(synchronize_session=False)
            return {"status": True, "data": {"tags": labels}}
        except Exception, e:
            logger.exception(str(e))
