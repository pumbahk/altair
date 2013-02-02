import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.page.models import Page, PageSet
from .models import PromotionTag
from datetime import datetime

class PromotionPageListSearcher(object):
    def __init__(self, request, finder,
                 search_key="search",
                 published="published", 
                 term_begin="term_begin", 
                 term_end="term_end", 
                 _now=datetime.now):
        self.request = request 
        self.finder = finder

        self.search_key=search_key
        self.published=published 
        self.term_begin=term_begin 
        self.term_end=term_end 

        self._now = _now

    def filter_default(self, qs, params):
        qs = self._filter_by_tag_label(qs, params)        
        qs = self._filter_by_page_term(qs, params)
        qs = self._filter_by_page_published(qs, params)
        return qs

    def no_filter_without_tag(self, qs, params):
        qs = self._filter_by_tag_label(qs, params)
        return qs

    def _filter_by_page_term(self, qs, params):
        if self.term_begin not in params and self.term_end not in params:
            now = self._now()
            return qs.filter(Page.in_term(now))

        if self.term_begin in params:
            qs = qs.filter(Page.publish_begin >= params[self.term_begin])
        elif self.term_end in params:
            qs = qs.filter(Page.publish_end <= params[self.term_end])
        return qs
    
    def _filter_by_page_published(self, qs, params):
        if self.published not in params:
            return qs
        return qs.filter(Page.published==params[self.published])

    def _filter_by_tag_label(self, qs, params):
        label = params.get(self.search_key)
        if label:
            return qs.filter(PromotionTag.label.like(u"%%%s%%" % label))
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
