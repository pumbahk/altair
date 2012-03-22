from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from . import renderable
from altaircms.lib.interception import not_support_if_keyerror

class PerformancelistWidget(Widget):
    implements(IWidget)
    type = "performancelist"

    template_name = "altaircms.plugins.widget:performancelist/render.mako"
    __tablename__ = "widget_performancelist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("performances")
        bsettings.need_extra_in_scan("request")
        @not_support_if_keyerror("performancelist widget: %(err)s")
        def performancelist_render():
            performances = bsettings.extra["performances"]
            request = bsettings.extra["request"]
            return renderable.PfListRenderable(self, performances, request).render()
        bsettings.add(bname, performancelist_render)

class PerformancelistWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = PerformancelistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PerformancelistWidget, widget_id)

