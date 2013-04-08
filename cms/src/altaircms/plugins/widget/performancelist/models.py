# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
from pyramid.renderers import render

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.plugins.widget.api import get_rendering_function_via_page

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.plugins.base.interception import not_support_if_keyerror

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
        ## lookup utilities.py
        bsettings.need_extra_in_scan("performances")
        closure = get_rendering_function_via_page(self, bname, bsettings, self.type)
        bsettings.add(bname, closure)


class PerformancelistWidgetResource(HandleSessionMixin,
                                    UpdateDataMixin,
                                    HandleWidgetMixin,
                                    RootFactory
                                    ):
    WidgetClass = PerformancelistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PerformancelistWidget, widget_id)

