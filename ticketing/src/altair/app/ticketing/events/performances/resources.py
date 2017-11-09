# -*- coding: utf-8 -*-

from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.decorator import reify
from pyramid.security import ACLAllowed
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.util import class_mapper
from sqlalchemy import sql

from altair.sqla import new_comparator
from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Organization, Event, Performance, SalesSegment, SalesSegmentSetting

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

    def sort_sales_segments(self):
        sort_column = self.request.GET.get('sort')
        query = SalesSegment.query.filter(SalesSegment.performance_id == self.request.matchdict.get('performance_id'))

        if sort_column == 'start_on':
            query = query.join(SalesSegmentSetting)
            md_class = SalesSegmentSetting
        else:
            md_class = SalesSegment
        try:
            mapper = class_mapper(md_class)
            prop = mapper.get_property(sort_column)
            sort = new_comparator(prop, mapper)

        except:
            sort = None
        direction = {'asc': sql.asc, 'desc': sql.desc}.get(
            self.request.GET.get('direction'),
            sql.asc
        )
        self.performance.sales_segments = query.order_by(direction(sort)).all()
        return None

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
