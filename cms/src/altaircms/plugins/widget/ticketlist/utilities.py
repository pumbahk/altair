# -*- coding:utf-8 -*-
import sqlalchemy as sa
import sqlalchemy.orm as orm
from functools import partial
from datetime import datetime
from pyramid.renderers import render
from zope.interface import implementer

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from .models import TicketlistWidget

from altaircms.models import Performance, SalesSegment, Ticket
def render_with_template(template_name, request, widget, event):
    if widget.target_performance_id:
        target_performance_id = widget.target_performance_id
    else:
        target_performance_id = Performance.query.filter(Performance.event_id==event.id).first().id

    if widget.target_salessegment_id:
        target_salessegment_id = widget.target_salessegment_id
    else:
        target_salessegment_id = SalesSegment.query.filter(SalesSegment.performance_id==target_performance_id).first().id

    tickets = Ticket.query.filter(Ticket.salessegment_id==target_salessegment_id)
    tickets = tickets.order_by(sa.asc(Ticket.display_order), sa.desc(Ticket.price))
    return render(template_name, {"widget": widget, "tickets": tickets}, request)

render_default = partial(render_with_template, "altaircms.plugins.widget:ticketlist/render.html")

@implementer(IWidgetUtility)
class TicketlistWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        self.settings = dict(configparser.items(TicketlistWidget.type))
        self.rendering = DisplayTypeSelectRendering(self.settings, configparser)

        self.rendering.register("default", render_default)
        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type or "default"
        return self.rendering.lookup(display_type, default="")(request, widget, bsettings.extra["event"])

