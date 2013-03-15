# -*- encoding:utf-8 -*-
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
from altaircms.plugins.widget.api import get_rendering_function_via_page

class TicketlistWidget(Widget):
    implements(IWidget)
    type = "ticketlist"

    template_name = "altaircms.plugins.widget:ticketlist/render.html"
    __tablename__ = "widget_ticketlist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    display_type = sa.Column(sa.Unicode(255))
    caption = sa.Column(sa.UnicodeText, doc=u"表に対する説明")
    target_performance_id = sa.Column(sa.Integer, sa.ForeignKey("performance.id"))
    target_performance = orm.relationship("Performance")
    target_salessegment_id = sa.Column(sa.Integer, sa.ForeignKey("sale.id"))
    target_salessegment = orm.relationship("SalesSegment")
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    show_label = sa.Column(sa.Boolean, doc=u"見出しを表示するか否かのフラグ", default=True, nullable=False)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("event")
        ## lookup utilities.py
        closure = get_rendering_function_via_page(self, bname, bsettings, self.type)
        bsettings.add(bname, closure)

class TicketlistWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = TicketlistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TicketlistWidget, widget_id)
