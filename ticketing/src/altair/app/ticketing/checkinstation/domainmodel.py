# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from altair.app.ticketing.core.models import Event, Performance
import sqlalchemy as sa

class ChoosableEvent(object):
    def __init__(self, request, operator):
        self.request = request
        self.operator = operator

    def choosable_event_query(self, now): #基準日時より前後は後で
        qs = (Event.query
              .filter_by(organization_id=self.operator.organization_id)
              .filter(Event.id==Performance.id)
              .filter(sa.or_(Performance.end_on>=now, Performance.end_on == None)))
        return qs.distinct(Event.id).order_by(sa.asc(Event.title))


