# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event, Performance
)
from pyramid.decorator import reify
from ..events.printed_reports import api
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound


class LiveStreamingResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id==self.performance_id,
                                        Performance.event_id==Event.id,
                                        Event.organization_id==self.organization.id).first()
