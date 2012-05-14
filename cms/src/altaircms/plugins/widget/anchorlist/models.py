# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import render

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from ..heading.api import collect_heading_widgets_from_page

class AnchorlistWidget(Widget):
    implements(IWidget)
    type = "anchorlist"

    template_name = "altaircms.plugins.widget:anchorlist/render.mako"
    __tablename__ = "widget_anchorlist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        def rendering_internallink_list():
            request = bsettings.extra["request"]
            page = bsettings.extra["page"]
            headings = collect_heading_widgets_from_page(page)
            params = {"page": page, "headings": list(headings)}
            return render(self.template_name, params, request=request)
        bsettings.add(bname, rendering_internallink_list)

class AnchorlistWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = AnchorlistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(AnchorlistWidget, widget_id)
