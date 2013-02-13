import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.decorator import reify

from altaircms.page.models import Page, PageSet
from .models import PromotionTag
from .models import TopcontentTag
from .models import TopicTag
from datetime import datetime

import altaircms.searchlib as sl
from altaircms.tag.api import get_tagmanager
from altaircms.tag.api import get_system_tagmanager

def qs_filter_using_conds_list(qs, conds_list):
    for conds in conds_list:
        qs = qs.filter(*conds)
    return qs

PromotionPageListSearchSchemaList = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

PromotionPageListTagOnly = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    ]

TopcontentPageListSearchSchemaList = [
    sl.LikeSearchSchema(TopcontentTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

TopcontentPageListTagOnly = [
    sl.LikeSearchSchema(TopcontentTag, "search", model_attribute="label"), 
    ]

TopicPageListSearchSchemaList = [
    sl.LikeSearchSchema(TopicTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

TopicPageListTagOnly = [
    sl.LikeSearchSchema(TopicTag, "search", model_attribute="label"), 
    ]

class TopicPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=datetime.now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopicPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now()
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopicPageListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def get_objects_for_grid(self, qs):
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

class TopcontentPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=datetime.now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopcontentPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now()
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(TopcontentPageListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def get_objects_for_grid(self, qs):
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

class PromotionPageListSearcher(object):
    def __init__(self, request, finder, 
                 _now=datetime.now):
        self.request = request 
        self.finder = finder
        self._now = _now

    def filter_default(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(PromotionPageListSearchSchemaList, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        now = self._now()
        return qs.filter(Page.in_term(now))

    def no_filter_without_tag(self, qs, params):
        cond_dict = sl.parse_params_using_schemas(PromotionPageListTagOnly, params)
        qs = qs_filter_using_conds_list(qs, cond_dict.itervalues())
        return qs

    def get_objects_for_grid(self, qs):
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

## global
class GlobalTopicSearcher(object):
    def __init__(self, TargetTopic, request):
        self.TargetTopic = TargetTopic
        assert TargetTopic.type
        self.type = TargetTopic.type
        self.request = request

    @reify
    def tagmanager(self):
        return get_tagmanager(self.type, request=self.request)

    @reify
    def system_tagmanager(self):
        return get_system_tagmanager(self.type, request=self.request)

    def _start_query(self):
        if hasattr(self.request, "allowable"):
            return self.request.allowable(self.TargetTopic)
        else:
            return self.TargetTopic.query

    def query_publishing(self, dt, qs=None):
        qs = qs or self._start_query()
        return self.TargetTopic.publishing(d=dt, qs=qs)

    def filter_by_tag(self, qs, tag):
        return self.tagmanager.more_filter_by_tag(qs, tag)

    def filter_by_system_tag(self, qs, tag):
        return self.system_tagmanager.more_filter_by_tag(qs, tag)

    def filter_by_genre_label(self, qs, genre_label):
        system_tag = self.get_tag_from_genre_label(genre_label)
        return self.system_tagmanager.more_filter_by_tag(qs, system_tag)

    def get_tag_from_genre_label(self, genre_label):
        return self.system_tagmanager.get_or_create_tag(genre_label, public_status=True)

