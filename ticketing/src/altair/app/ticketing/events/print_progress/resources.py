# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Event
from pyramid.decorator import reify

class EventPrintProgressResource(TicketingAdminResource):
    @property
    def event_id(self):
        return self.request.matchdict["event_id"]

    @reify
    def target(self):
        return Event.query.filter(Event.id==self.event_id,
                           Event.organization_id==self.organization.id).first()

