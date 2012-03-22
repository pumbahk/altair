from zope.interface import implements
from altaircms.interfaces import IWidget
import json
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.page.models import Page
import altaircms.helpers as h
from altaircms.lib.interception import not_support_if_keyerror

class MenuWidget(Widget):
    implements(IWidget)
    type = "menu"

    template_name = "altaircms.plugins.widget:menu/render.mako"
    __tablename__ = "widget_menu"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    items = sa.Column(sa.String) #json string
    

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        @not_support_if_keyerror("menu widget: %(err)s")
        def tab_render():
            from pyramid.renderers import render
            request = bsettings.extra["request"]
            thispage = bsettings.extra["page"]
            items = json.loads(self.items)
            params = {"widget":self, "items": items, "thispage": thispage}
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

    def _items_from_page(self, page):
        to_url = h.front.to_preview_page
        return json.dumps( [{"label": p.title, "link": to_url(self.request, p)} for p in page.event.pages])        

    def get_items(self, page_id):
        page = Page.query.filter(Page.id==page_id).one()
        return self._items_from_page(page) if page.event else "[]"

