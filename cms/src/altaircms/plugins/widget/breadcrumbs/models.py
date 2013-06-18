from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import render
from altaircms.modelmanager.ancestors import GetWithGenrePagesetAncestor
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.plugins.base.interception import not_support_if_keyerror

class BreadcrumbsWidget(Widget):
    implements(IWidget)
    type = "breadcrumbs"

    template_name = "altaircms.plugins.widget:breadcrumbs/render.html"
    __tablename__ = "widget_breadcrumbs"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def get_ancestor_pages(self, page):
        root = page.pageset
        return GetWithGenrePagesetAncestor(root).get_ancestors()

    @not_support_if_keyerror("breadcrumbs widget: %(err)s")
    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        def breadcrumbs_render():
            request = bsettings.extra["request"]
            page = bsettings.extra["page"]
            return render(self.template_name, {"request":request, "page":page, "widget":self}, request)
        bsettings.add(bname, breadcrumbs_render)

class BreadcrumbsWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = BreadcrumbsWidget

    def get_widget(self, widget_id):
        return self._get_or_create(BreadcrumbsWidget, widget_id)
