# -*- coding:utf-8 -*-

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

## kind = divのクラス名として展開(todo整理)
KINDS = ["description", "dummy"]

class DetailWidget(Widget):
    implements(IWidget)
    type = "detail"
    
    __tablename__ = "widget_detail"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.String(255))
    
    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("event")
        bsettings.need_extra_in_scan("performances")
        @not_support_if_keyerror("detail widget: %(err)s")
        def detail_render():
            request = bsettings.extra["request"]
            performances = bsettings.extra["performances"]
            event = bsettings.extra["event"]
            render =  getattr(renderable, self.kind)
            return render(self, request, ctx={"event": event, "performances": performances}).render()
        bsettings.add(bname, detail_render)

class DetailWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = DetailWidget

    def get_widget(self, widget_id):
        return self._get_or_create(DetailWidget, widget_id)

    def attach_form_from_widget(self, D, widget):
        form = D["form_class"](**widget.to_dict())
        D["form"] = form
        return D
