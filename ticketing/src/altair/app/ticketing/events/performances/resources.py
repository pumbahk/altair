# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Organization, Event, Performance

class PerformanceAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(PerformanceAdminResource, self).__init__(request)

        if not self.user:
            return

        self.performance = None
        self.event = None

        performance_id = self.request.matchdict.get('performance_id', None)
        if performance_id is not None:
            try:
                performance_id = long(performance_id)
                self.performance = Performance.query\
                    .join(Performance.event)\
                    .join(Event.organization)\
                    .filter(Organization.id == self.user.organization_id)\
                    .filter(Performance.id == performance_id)\
                    .one()
            except (TypeError, ValueError):
                pass
            except NoResultFound:
                pass
            if self.performance is None:
                raise HTTPNotFound('performance id %s is not found' % performance_id)

        event_id = self.request.matchdict.get('event_id', None)
        if event_id is not None:
            slave_session = get_db_session(self.request, name="slave")
            try:
                event_id = long(event_id)
                self.event = slave_session.query(Event).filter(
                    Event.id==event_id,
                    Event.organization_id==self.user.organization_id
                ).one()
            except (TypeError, ValueError):
                pass
            except NoResultFound:
                pass
            if self.event is None:
                raise HTTPNotFound('event id %s is not found' % event_id)
