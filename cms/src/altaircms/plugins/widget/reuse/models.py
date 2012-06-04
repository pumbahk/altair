# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
from pyramid.view import render_view_to_response
import sqlalchemy as sa
import sqlalchemy.orm as orm
import json

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from pyramid.renderers import render

class ReuseWidget(Widget):
    implements(IWidget)
    type = "reuse"

    template_name = "altaircms.plugins.widget:reuse/render.mako"

    attrs = sa.Column(sa.String(255), default='{"class": "reuse-widget"}') #json'{"class": "foo" "id": "bar"}'
    source_page_id = sa.Column(sa.Integer, sa.ForeignKey("page.id"))
    source_page = orm.relationship("Page", backref="reuse_widgets")
    width = sa.Column(sa.Integer, nullable=True)
    height = sa.Column(sa.Integer, nullable=True)

    __tablename__ = "widget_reuse"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    @property
    def attributes(self):
        if hasattr(self, "_attributes"):
            return self._attributes
        self._attributes = json.loads(self.attrs)
        return self._attributes


    def _get_internal_content(self, request):
        request._reuse_widget = self
        ## widgetが持っているpageをレンダリングするviewを呼ぶ
        response = render_view_to_response(None, request, name="reuse_redering_source_page_only")# .views
        return response.ubody

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        def reuse_render():
            request = bsettings.extra["request"]            
            content = self._get_internal_content(request)
            return render(self.template_name, {"content": content, "widget":self}, request)                    
        bsettings.add(bname, reuse_render)

        ## サイズを調節するcssを挿入
        for v in ["width", "height"]: #ugly
            if getattr(self, v, None):
                if "id" in self.attributes:
                    bsettings.add("css_prerender", "//reuse widget \n #%s {%s: %s;}" % (v, self.attributes["id"], self.width))
                if "class" in self.attributes:
                    bsettings.add("css_prerender", "//reuse widget \n .%s {%s: %s;}" % (v, self.attributes["class"], self.width))

class ReuseWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = ReuseWidget

    def get_widget(self, widget_id):
        return self._get_or_create(ReuseWidget, widget_id)
