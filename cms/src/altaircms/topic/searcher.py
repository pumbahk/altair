from zope.deprecation import deprecate
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.page.models import Page, PageSet
from .models import PromotionTag, TopcontentTag, TopicTag
from .models import Promotion, Topcontent, Topic
from altaircms.datelib import get_now

import altaircms.searchlib as sl
from altaircms.tag.api import get_tagmanager
from ..modelmanager.searcher import PublishingModelSearcher


def qs_filter_using_conds_list(qs, conds_list):
    for conds in conds_list:
        qs = qs.filter(*conds)
    return qs

PromotionUnitListSearchSchemaList = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Promotion, "term_begin", model_attribute="publish_open_on"), 
    sl.DateTimeMaybeSearchSchema(Promotion, "term_end", model_attribute="publish_close_on"), 
    sl.ComplementSearchSchema(Promotion, "is_vetoed")
]

PromotionPageListSearchSchemaList = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

PromotionListTagOnly = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    ]
TopcontentUnitListSearchSchemaList = [
    sl.LikeSearchSchema(TopcontentTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Topcontent, "term_begin", model_attribute="publish_open_on"), 
    sl.DateTimeMaybeSearchSchema(Topcontent, "term_end", model_attribute="publish_close_on"), 
    sl.ComplementSearchSchema(Topcontent, "is_vetoed")
]

TopcontentPageListSearchSchemaList = [
    sl.LikeSearchSchema(TopcontentTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

TopcontentListTagOnly = [
    sl.LikeSearchSchema(TopcontentTag, "search", model_attribute="label"), 
    ]

TopicUnitListSearchSchemaList = [
    sl.LikeSearchSchema(TopicTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Topic, "term_begin", model_attribute="publish_open_on"), 
    sl.DateTimeMaybeSearchSchema(Topic, "term_end", model_attribute="publish_close_on"), 
    sl.ComplementSearchSchema(Topic, "is_vetoed")
]

TopicPageListSearchSchemaList = [
    sl.LikeSearchSchema(TopicTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

TopicListTagOnly = [
    sl.LikeSearchSchema(TopicTag, "search", model_attribute="label"), 
    ]

class TopicUnitListSearcher(object):
    def __init__(self, request, _now=get_now):
        self.request = request 
        self._now = _now

    def filter_default(self, qs, params):
        params = params.copy()
        now = self._now(self.request)
        params["term_end__gte"] = params["term_begin__lte"] = now
        cond_dict = sl.parse_params_using_schemas(TopicUnitListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopicListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        return get_tagmanager(Topic.type, request=self.request).joined_query(qs=qs)

class TopicPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=get_now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopicPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now(self.request)
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopicListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        qs = qs.filter(PageSet.id==Page.pageset_id).filter(self.finder.widget.tag_id==TopicTag.id)
        qs = qs.with_entities(PageSet, Page, self.finder.widget, TopicTag)
        qs = qs.options(orm.joinedload(self.finder.widget.system_tag)).order_by(sa.desc(PageSet.updated_at), sa.desc(Page.updated_at))
        return qs

class TopicPageDetailSearcher(object):
    def __init__(self, request, finder):
        self.request = request 
        self.finder = finder

    def get_widgets(self, page_id):
        return self.finder.widget.query.filter_by(page_id=page_id)

    def get_current_widget(self, widgets, widget_id=None):
        if widget_id:
            return widgets.filter(self.finder.widget.id==widget_id).first()
        return widgets.first()



class TopcontentUnitListSearcher(object):
    def __init__(self, request, _now=get_now):
        self.request = request 
        self._now = _now

    def filter_default(self, qs, params):
        params = params.copy()
        now = self._now(self.request)
        params["term_end__gte"] = params["term_begin__lte"] = now
        cond_dict = sl.parse_params_using_schemas(TopcontentUnitListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopcontentListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        return get_tagmanager(Topcontent.type, request=self.request).joined_query(qs=qs)

class TopcontentPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=get_now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopcontentPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now(self.request)
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopcontentListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        qs = qs.filter(PageSet.id==Page.pageset_id).filter(self.finder.widget.tag_id==TopcontentTag.id)
        qs = qs.with_entities(PageSet, Page, self.finder.widget, TopcontentTag)
        qs = qs.options(orm.joinedload(self.finder.widget.system_tag)).order_by(sa.desc(PageSet.updated_at), sa.desc(Page.updated_at))
        return qs

class TopcontentPageDetailSearcher(object):
    def __init__(self, request, finder):
        self.request = request 
        self.finder = finder

    def get_widgets(self, page_id):
        return self.finder.widget.query.filter_by(page_id=page_id)

    def get_current_widget(self, widgets, widget_id=None):
        if widget_id:
            return widgets.filter(self.finder.widget.id==widget_id).first()
        return widgets.first()


class PromotionUnitListSearcher(object):
    def __init__(self, request, _now=get_now):
        self.request = request 
        self._now = _now

    def filter_default(self, qs, params):
        params = params.copy()
        now = self._now(self.request)
        params["term_end__gte"] = params["term_begin__lte"] = now
        cond_dict = sl.parse_params_using_schemas(PromotionUnitListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(PromotionListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        return get_tagmanager(Promotion.type, request=self.request).joined_query(qs=qs)


class PromotionPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=get_now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(PromotionPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now(self.request)
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(PromotionListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def query_objects_for_grid(self, qs):
        qs = qs.filter(PageSet.id==Page.pageset_id).filter(self.finder.widget.tag_id==PromotionTag.id)
        qs = qs.with_entities(PageSet, Page, self.finder.widget, PromotionTag)
        qs = qs.options(orm.joinedload(self.finder.widget.system_tag)).order_by(sa.desc(PageSet.updated_at), sa.desc(Page.updated_at))
        return qs

class PromotionPageDetailSearcher(object):
    def __init__(self, request, finder):
        self.request = request 
        self.finder = finder

    def get_widgets(self, page_id):
        return self.finder.widget.query.filter_by(page_id=page_id)

    def get_current_widget(self, widgets, widget_id=None):
        if widget_id:
            return widgets.filter(self.finder.widget.id==widget_id).first()
        return widgets.first()

class GlobalTopicSearcher(PublishingModelSearcher):
    """ for backward compability"""
    @deprecate("GlobalTopicSearcher is obsolute. please using PublishingModelSearcher")
    @property
    def TargetTopic(self):
        return self.TargetModel

    @deprecate("rename query_publishing_topics -> query_publishing")
    def query_publishing_topics(self, dt, tag, system_tag=None): #system_tag is tag
        return self.query_publishing(dt, tag, system_tag=system_tag)
    
