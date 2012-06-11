from zope.interface import implements
from pyramid.renderers import render

from altaircms.interfaces import IWidget
import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.models import Sale, Ticket
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

    kind = sa.Column(sa.Unicode(255))
    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("event")
        @not_support_if_keyerror("ticketlist widget: %(err)s")
        def ticketlist_render():
            request = bsettings.extra["request"]
            event = bsettings.extra["event"]

            sale = Sale.query.filter(Sale.kind==self.kind).filter(Sale.event==event).first()
            tickets = sale.tickets if sale else []
            params = {"widget":self, "event": event, "sale":sale, "tickets": tickets}
            
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
