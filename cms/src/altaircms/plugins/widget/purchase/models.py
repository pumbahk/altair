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
import altaircms.helpers as h

def purchase_simple_render(request, widget, event):
    if widget.external_link:
        href = widget.external_link
    else:
        href = h.link.get_purchase_page_from_event(request, event)  
    return u'<a href="%s"><div class="purchase-simple"></div></a>' % href

PURCHASE_DISPATCH = {
    "simple": purchase_simple_render, 
    }
PURCHASE_KIND_CHOICES = [(x, x) for x in PURCHASE_DISPATCH.keys()]

class PurchaseWidget(Widget):
    implements(IWidget)
    type = "purchase"

    template_name = "altaircms.plugins.widget:purchase/render.mako"
    __tablename__ = "widget_purchase"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(32))
    external_link = sa.Column(sa.Unicode(255))

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("event")
        bsettings.need_extra_in_scan("request")
        def render_purchase_button():
            event = bsettings.extra["event"]
            request = bsettings.extra["request"]
            return PURCHASE_DISPATCH[self.kind](request, self, event)
        bsettings.add(bname, render_purchase_button)

class PurchaseWidgetResource(HandleSessionMixin,
                             UpdateDataMixin,
                             HandleWidgetMixin,
                             RootFactory
                             ):
    WidgetClass = PurchaseWidget

    def get_widget(self, widget_id):
        return self._get_or_create(PurchaseWidget, widget_id)
