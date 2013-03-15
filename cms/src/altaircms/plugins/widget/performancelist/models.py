# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
from pyramid.renderers import render

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.plugins.base.interception import not_support_if_keyerror


## todo refactoring
WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def render_fullset(widget, bname, bsettings):
    """ rendering: title,  iconset,  performance list
    """
    template_name = "altaircms.plugins.widget:performancelist/render.html"
    bsettings.need_extra_in_scan("performances")
    bsettings.need_extra_in_scan("event")
    bsettings.need_extra_in_scan("request")

    @not_support_if_keyerror("performancelist widget: %(err)s")
    def performancelist_render():
        performances = bsettings.extra["performances"]
        event = bsettings.extra["event"]
        request = bsettings.extra["request"]
        icon_classes = event.service_info_list
        return render(template_name, 
                      {"performances": performances, 
                       "event": event, 
                       "widget": widget, 
                       "icon_classes": icon_classes, 
                       "WEEK": WEEK}, 
                      request)
    bsettings.add(bname, performancelist_render)

MERGE_SETTINGS_DISPATH = {
    "fullset": render_fullset
    }

PERFORMANCELIST_KIND_CHOICES = [("fullset", u"デフォルト")]

class PerformancelistWidget(Widget):
    implements(IWidget)
    type = "performancelist"
    __tablename__ = "widget_performancelist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(32))
    mask_performance_date = sa.Column(sa.Boolean, default=False, nullable=False)

    def merge_settings(self, bname, bsettings):
        merge_settings_function = MERGE_SETTINGS_DISPATH.get(self.kind) or MERGE_SETTINGS_DISPATH["fullset"]
        merge_settings_function(self, bname, bsettings)

class PerformancelistWidgetResource(HandleSessionMixin,
                                    UpdateDataMixin,
                                    HandleWidgetMixin,
                                    RootFactory
                                    ):
    WidgetClass = PerformancelistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PerformancelistWidget, widget_id)

