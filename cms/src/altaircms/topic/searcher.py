import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.page.models import Page, PageSet
from .models import PromotionTag
from datetime import datetime

import altaircms.searchlib as sl

PromotionPageListSearchSchemaList = [
    sl.LikeSearchSchema(PromotionTag, "search", model_attribute="label"), 
    sl.DateTimeSearchSchema(Page, "term_begin", model_attribute="publish_begin"), 
    sl.DateTimeMaybeSearchSchema(Page, "term_end", model_attribute="publish_end"), 
    sl.BooleanSearchSchema(Page, "published")
    ]

PromotionPageListTagOnly = [
    sl.LikeSearchSchema(PromotionTag, "label"), 
    ]


def qs_filter_using_conds_list(qs, conds_list):
    for conds in conds_list:
        qs = qs.filter(*conds)
    return qs

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
        qs = qs.filter(PageSet.id==Page.pageset_id).filter(self.finder.widget.kind_id==PromotionTag.id)
        qs = qs.with_entities(PageSet, Page, self.finder.widget, PromotionTag)
        qs = qs.options(orm.joinedload(Page.pageset)).order_by(sa.asc(PageSet.id), sa.asc(Page.id))
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
