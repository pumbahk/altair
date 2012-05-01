# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from zope.interface import implements
from altaircms.interfaces import IWidget
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from .api import get_linklist_candidates_finder

def linklist_render(widget, finder, request=None):
    candidates = finder.find(request, widget.N, widget._today_function(), max_items=widget.max_items)
    content = widget.delimiter.join(candidates)
    return u'<div id="%s"><p>%s</p></div>' % (widget.finder_kind, content)
    
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

    FINDER_KINDS_DICT= {u"販売終了間近": "nearTheEnd", 
                        u"今週販売のチケット": "thisWeek"}

    ## fixme
    max_items = sa.Column(sa.Integer, default=20)
    N = 7
    
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
