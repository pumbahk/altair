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

class MenuWidget(Widget):
    implements(IWidget)
    type = "menu"

    template_name = "altaircms.plugins.widget:menu/render.mako"
    __tablename__ = "widget_menu"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        bsettings.need_extra_in_scan("event")
        def tab_render():
            from pyramid.renderers import render
            request = bsettings.extra["request"]
            event = bsettings.extra["event"]
            thispage = bsettings.extra["page"]
            params = {"widget":self, "event": event, "pages": event.pages, "thispage": thispage}
            return render(self.template_name, params, request)
        bsettings.add(bname, tab_render)


class MenuWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = MenuWidget

    def get_widget(self, widget_id):
        return self._get_or_create(MenuWidget, widget_id)
