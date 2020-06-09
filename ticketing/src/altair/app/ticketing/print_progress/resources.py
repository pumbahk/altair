# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event, Performance
)
from pyramid.decorator import reify
from ..events.printed_reports import api
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound
from .cipher import AESCipher

AES_KEY = "cthTUEstfg890CVfA7LKjV6ThuwkwHCRom5Pki0Dg1IGoeqIt3"


class EventPrintProgressResource(TicketingAdminResource):
    def __init__(self, request):
        super(EventPrintProgressResource, self).__init__(request)
        self.cipher = AESCipher(AES_KEY)
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

    @property
    def encrypt_event_id(self):
        return self.cipher.encrypt(self.request.matchdict["event_id"])

    @property
    def encevent_id(self):
        return self.request.matchdict["event_id"]

    @reify
    def performance_id_list(self):
        return [p.id for p in self.target.performances]

    @reify
    def target(self):
        return Event.query.filter(Event.id == self.event_id,
                                  Event.organization_id == self.organization.id).first()

    @reify
    def printed_report_setting(self):
        return self.printed_report_setting


class PerformancePrintProgressResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id == self.performance_id,
                                        Performance.event_id == Event.id,
                                        Event.organization_id == self.organization.id).first()


class EventPrintProgressEasyResource(TicketingAdminResource):

    def __init__(self, request):
        super(EventPrintProgressEasyResource, self).__init__(request)
        self.cipher = AESCipher(AES_KEY)
        try:
            hash_event_id = self.request.matchdict.get('hash_event_id')
            event_id = self.cipher.decrypt(hash_event_id)
            self.event = Event.query.filter(Event.id == event_id).one()
        except (TypeError, ValueError, NoResultFound):
            raise HTTPNotFound()
        self.printed_report_setting = api.get_or_create_printed_report_setting(request, self.event, self.user)

    @property
    def event_id(self):
        hash_event_id = self.request.matchdict["hash_event_id"]
        return self.cipher.decrypt(hash_event_id)

    @reify
    def performance_id_list(self):
        return [p.id for p in self.target.performances]

    @reify
    def target(self):
        return Event.query.filter(Event.id == self.event_id).first()

    @reify
    def printed_report_setting(self):
        return self.printed_report_setting


class PerformancePrintProgressEasyResource(TicketingAdminResource):

    def __init__(self, request):
        super(PerformancePrintProgressEasyResource, self).__init__(request)
        self.cipher = AESCipher(AES_KEY)

    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id == self.performance_id,
                                        Performance.event_id == Event.id,
                                        Event.organization_id == self.organization.id).first()
