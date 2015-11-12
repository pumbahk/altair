# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event, Performance
)
from pyramid.decorator import reify

class EventPrintProgressResource(TicketingAdminResource):
    @property
    def event_id(self):
        return self.request.matchdict["event_id"]

    @reify
    def performance_id_list(self):
        return [p.id for p in self.target.performances]

    @reify
    def target(self):
        return Event.query.filter(Event.id==self.event_id,
                           Event.organization_id==self.organization.id).first()

class PerformancePrintProgressResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id==self.performance_id,
                                        Performance.event_id==Event.id,
                                        Event.organization_id==self.organization.id).first()
