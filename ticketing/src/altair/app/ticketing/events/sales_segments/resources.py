from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, Performance, Event, Organization

class SalesSegmentAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(SalesSegmentAdminResource, self).__init__(request)

        event_id = None
        sales_segment_id = None
        sales_segment_group_id = None
        performance_id = None

        if not self.user:
            return

        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_id = long(self.request.matchdict.get('sales_segment_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_group_id = long(self.request.params.get('sales_segment_group_id'))
        except (TypeError, ValueError):
            pass

        try:
            performance_id = long(self.request.params.get('performance_id'))
        except (TypeError, ValueError):
            pass

        if event_id is not None:
            self.event = Event.query \
                .join(Event.organization) \
                .filter(Organization.id == self.user.organization_id) \
                .filter(Event.id == event_id) \
                .one()
        else:
            self.event = None

        if performance_id is not None:
            self.performance = Performance.query \
                .join(Performance.event) \
                .join(Event.organization) \
                .filter(Organization.id == self.user.organization_id) \
                .filter(Performance.id == performance_id) \
                .one()

            if self.event is not None and \
               self.performance.event_id != self.event.id:
                raise Exception() # XXX
            if self.event is None:
                self.event = self.performance.event
        else:
            self.performance = None

        if sales_segment_group_id is not None:
            self.sales_segment_group = SalesSegmentGroup.query \
                .join(SalesSegmentGroup.event) \
                .join(Event.organization) \
                .filter(Organization.id == self.user.organization_id) \
                .filter(SalesSegmentGroup.id == sales_segment_group_id) \
                .one()

            if self.event is not None and \
               self.sales_segment_group.event_id != self.event.id:
                raise Exception() # XXX
            if self.event is None:
                self.event = self.sales_segment_group.event
        else:
            self.sales_segment_group = None

        if sales_segment_id is not None:
            self.sales_segment = SalesSegment.query \
                .join(SalesSegment.sales_segment_group) \
                .join(SalesSegmentGroup.event) \
                .join(Event.organization) \
                .filter(Organization.id == self.user.organization_id) \
                .filter(SalesSegment.id == sales_segment_id) \
                .one()

            if (self.sales_segment_group is not None and \
                self.sales_segment.sales_segment_group_id != self.sales_segment_group.id) or \
               (self.performance is not None and \
                self.sales_segment.performance_id != self.performance.id):
                raise Exception() # XXX
            if self.sales_segment_group is None:
                self.sales_segment_group = self.sales_segment.sales_segment_group
            if self.event is None:
                self.event = self.sales_segment_group.event
            if self.performance is None:
                self.performance = self.sales_segment.performance
        else:
            self.sales_segment = None
