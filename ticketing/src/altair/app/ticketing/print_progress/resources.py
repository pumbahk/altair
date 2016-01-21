# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event, Performance
)
from pyramid.decorator import reify
from ..events.printed_reports import api
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound


class EventPrintProgressResource(TicketingAdminResource):
    def __init__(self, request):
        super(EventPrintProgressResource, self).__init__(request)
        if not self.user:
            raise HTTPNotFound()

        try:
            event_id = long(self.request.matchdict.get('event_id'))
            self.event = Event.query.filter(Event.id == event_id).one()
        except (TypeError, ValueError, NoResultFound):
            raise HTTPNotFound()

        self.printed_report_setting = api.get_or_create_printed_report_setting(request, self.event, self.user)

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

    @reify
    def printed_report_setting(self):
        return self.printed_report_setting


class PerformancePrintProgressResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id==self.performance_id,
                                        Performance.event_id==Event.id,
                                        Event.organization_id==self.organization.id).first()
