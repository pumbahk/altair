# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import Performance, Event
import sqlalchemy as sa
import sqlalchemy.orm as orm

##qrappのapiを使う
from altair.app.ticketing.printqr.utils import ticketdata_from_qrdata
from altair.app.ticketing.qr import get_qrdata_builder

class TicketData(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def ticket_data_from_qrcode(self, signed):
        builder = get_qrdata_builder(self.request)
        qrdata = ticketdata_from_qrdata(builder.data_from_signed(signed))
        return ticketdata_from_qrdata(qrdata)

class ChoosablePerformance(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def choosable_performance_query(self, now): #基準日時より前後は後で
        qs = (Performance.query
              .filter(Performance.event_id==Event.id, Event.organization_id==self.operator.organization_id)
              .filter(Performance.id==Performance.id)
              .filter(sa.or_(Performance.end_on>=now, Performance.end_on == None)))
        qs = qs.options(orm.joinedload(Performance.event))
        return qs.distinct(Performance.id).order_by(sa.asc(Performance.start_on))


