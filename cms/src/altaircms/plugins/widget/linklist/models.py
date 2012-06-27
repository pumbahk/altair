# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from zope.interface import implements
from altaircms.interfaces import IWidget
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.page.models import PageSet
from altaircms.models import Category
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from .api import get_linklist_candidates_finder

def linklist_render(widget, finder, request=None):
    qs = finder(request, widget.limit_span or widget.N, widget._today_function())
    if widget.genre:
        qs = qs.filter(PageSet.id==Category.pageset_id).filter(Category.origin==widget.genre)
    if widget.max_items:
        qs = qs.limit(widget.max_items)

    candidates = [u'<a href="%s">%s</a>' % (h.link.publish_page_from_pageset(request, p), p.name) for p in qs]
    content = widget.delimiter.join(candidates)
    element = u'<p>%s</p>' % content if content else ''
    return u'<div id="%s">%s</div>' % (widget.finder_kind, element)


FINDER_KINDS_DICT= {"nearTheEnd": u"販売終了間近" , 
                    "thisWeek": u"今週販売のチケット"}


class LinklistWidget(Widget):
    _today_function = datetime.now
    implements(IWidget)
    type = "linklist"

    template_name = "altaircms.plugins.widget:linklist/render.mako"
    __tablename__ = "widget_linklist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    delimiter = sa.Column(sa.Unicode(255), default=u"/")
    finder_kind = sa.Column(sa.Unicode(32))

    ## fixme
    max_items = sa.Column(sa.Integer, default=20)
    limit_span = sa.Column(sa.Integer, default=7)
    genre = sa.Column(sa.Unicode(255))
    # category_id = sa.Column(sa.Integer, sa.ForeignKey("category.id"))
    # category = orm.relationship("Category")

    N = 7 ## default
    
    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        def render():
            request = bsettings.extra["request"]
            finder = get_linklist_candidates_finder(request, self.finder_kind)

            logger.debug(u"linklist: " + self.finder_kind)
            return linklist_render(self, finder, request=request)
        bsettings.add(bname, render)

class LinklistWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = LinklistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(LinklistWidget, widget_id)
