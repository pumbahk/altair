# -*- coding: utf-8 -*-

from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.decorator import reify
from pyramid.security import ACLAllowed
from sqlalchemy.orm.exc import NoResultFound

from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Organization, Event, Performance

class SalesCounterResourceMixin(object):
    @reify
    def _is_event_editor(self):
        return isinstance(self.request.has_permission('event_editor', self), ACLAllowed)

    @reify
    def available_sales_segments(self):
        def sales_segment_sort_key_func(ss):
            return (
                ss.kind == u'sales_counter',
                ss.start_at is None or ss.start_at <= self.now,
                ss.end_at is None or self.now <= ss.end_at,
                -ss.start_at.toordinal() if ss.start_at else 0,
                ss.sales_segment_group.name,
                ss.id
                )
        if not self._is_event_editor:
            sales_segments = [ss for ss in self.performance.sales_segments if ss.setting.sales_counter_selectable]
        else:
            sales_segments = self.performance.sales_segments 
        return sorted(sales_segments, key=sales_segment_sort_key_func, reverse=True)



class PerformanceAdminResource(TicketingAdminResource, SalesCounterResourceMixin):
    def __init__(self, request):
        super(PerformanceAdminResource, self).__init__(request)

        if not self.user:
            return

        self.performance = None
        self.event = None
        self.now = datetime.now()

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
