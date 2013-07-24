# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from zope.interface import implements
from altaircms.interfaces import IWidget
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.page.models import PageSet
from altaircms.page.models import PageTag2Page
from altaircms.page.models import PageTag
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from .api import get_linklist_candidates_finder
from altaircms.datelib import get_now
from datetime import datetime

def linklist_render(widget, finder, request=None):
    now = get_now(request)
    qs = finder(request, widget.limit_span or widget.N, now)
    if widget.system_tag_id:
        qs = qs.filter(PageTag2Page.object_id==PageSet.id, PageTag2Page.tag_id==widget.system_tag_id)
    if widget.max_items:
        qs = qs.limit(widget.max_items)
    qs = qs.all()
    if not qs:
        return u'<div id="%s"><p>現在、対象となる公演情報はありません</p></div>' % widget.finder_kind
    candidates = [u'<a href="%s">%s</a>' % (h.link.publish_page_from_pageset(request, p), p.name) for p in qs]
    content = widget.delimiter.join(candidates)
    element = u'<p>%s</p>' % content if content else ''
    return u'<div id="%s">%s</div>' % (widget.finder_kind, element)


FINDER_KINDS_DICT= {"nearTheEnd": u"販売終了間近" , 
                    "thisWeek": u"今週販売のチケット"}


class LinklistWidget(Widget):
    implements(IWidget)
    type = "linklist"

    template_name = "altaircms.plugins.widget:linklist/render.html"
    __tablename__ = "widget_linklist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    def __init__(self, *args, **kwargs):
        super(LinklistWidget, self).__init__(*args, **kwargs)
        if not "limit_span"  in kwargs:
            self.limit_span = 7
        if not "max_items"  in kwargs:
            self.max_items = 20

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    delimiter = sa.Column(sa.Unicode(255), default=u"/")
    finder_kind = sa.Column(sa.Unicode(32))

    ## fixme
    N = 7 ## default
    max_items = sa.Column(sa.Integer, default=20)
    limit_span = sa.Column(sa.Integer, default=7)
    system_tag_id = sa.Column(sa.Integer, sa.ForeignKey("pagetag.id"))
    system_tag = orm.relationship(PageTag, uselist=False, primaryjoin="LinklistWidget.system_tag_id==PageTag.id")

    
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
    Tag = PageTag
    def get_widget(self, widget_id):
        return self._get_or_create(LinklistWidget, widget_id)
