# -*- encoding:utf-8 -*-

from zope.interface import implements
from pyramid.renderers import render

from altaircms.interfaces import IWidget
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.models import Sale, Ticket, Performance
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.lib.interception import not_support_if_keyerror
from altaircms.seeds.saleskind import SALESKIND_CHOICES

class TicketlistWidget(Widget):
    implements(IWidget)
    type = "ticketlist"

    template_name = "altaircms.plugins.widget:ticketlist/render.mako"
    __tablename__ = "widget_ticketlist"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    kind = sa.Column(sa.Unicode(255), default="normal")
    caption = sa.Column(sa.UnicodeText, doc=u"見出し")
    target_performance_id = sa.Column(sa.Integer, sa.ForeignKey("performance.id"))
    target_performance = orm.relationship("Performance")

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        @not_support_if_keyerror("ticketlist widget: %(err)s")
        def ticketlist_render():
            request = bsettings.extra["request"]
            tickets = Ticket.query.filter(Ticket.performances.any(id=self.target_performance.id))
            tickets = tickets.filter(Sale.kind==self.kind).filter(Sale.id==Ticket.sale_id)
            tickets = tickets.order_by(sa.desc("price"))
            params = {"widget":self, "tickets": tickets}
            return render(self.template_name, params, request)
        bsettings.add(bname, ticketlist_render)

class TicketlistWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = TicketlistWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TicketlistWidget, widget_id)
