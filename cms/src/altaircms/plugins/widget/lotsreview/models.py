# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.plugins.widget.api import safe_execute
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from altaircms.modellib import MutationDict, JSONEncodedDict

def lotsreview_simple_render(request, widget, event):
    if widget.external_link:
        href = widget.external_link
    else:
        href = "http://rt.tstar.jp/lots/review"
        if request.organization.code != u"RT":
            href = "http://{0}/lots/review".format(request.host)
    return u'<div style="text-align:{0}"><a href="{1}" target="_blank"><img src="{2}"></a></div>'.format(widget.attributes['align'], href, request.static_url("altaircms:static/RT/img/lots/lotsreviewSimple.jpg"))

LOTSREVIEW_DISPATCH = {
    "simple": lotsreview_simple_render,
    }
LOTSREVIEW_KIND_CHOICES = [(x, x) for x in LOTSREVIEW_DISPATCH.keys()]

class LotsreviewWidget(Widget):
    implements(IWidget)
    type = "lotsreview"

    template_name = "altaircms.plugins.widget:lotsreview/render.html"
    __tablename__ = "widget_lotsreview"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(32))
    external_link = sa.Column(sa.Unicode(255))
    attributes = sa.Column(MutationDict.as_mutable(JSONEncodedDict(255)))

    @property
    def html_attributes(self):
        attributes = {}
        if self.attributes:
            attributes.update(self.attributes)
        return u" ".join([u'%s="%s"' % (k, v) for k, v in attributes.items()])

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("event")
        bsettings.need_extra_in_scan("request")
        @safe_execute("lotsreview")
        def render_lotsreview_button():
            event = bsettings.extra["event"]
            request = bsettings.extra["request"]
            return LOTSREVIEW_DISPATCH[self.kind](request, self, event)
        bsettings.add(bname, render_lotsreview_button)

class LotsreviewWidgetResource(HandleSessionMixin,
                             UpdateDataMixin,
                             HandleWidgetMixin,
                             RootFactory
                             ):
    WidgetClass = LotsreviewWidget

    def get_widget(self, widget_id):
        return self._get_or_create(LotsreviewWidget, widget_id)
