from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Organization, Event, Performance, SalesSegment, SalesSegmentGroup
from .models import PointGrantSetting

class PointGrantSettingAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(PointGrantSettingAdminResource, self).__init__(request)

        point_grant_setting_id = None
        event_id = None
        sales_segment_id = None
        sales_segment_group_id = None
        performance_id = None

        try:
            point_grant_setting_id = long(self.request.matchdict.get('point_grant_setting_id'))
        except (TypeError, ValueError):
            pass

        try:
            event_id = long(self.request.params.get('event_id'))
        except (TypeError, ValueError):
            pass

        try:
            sales_segment_id = long(self.request.params.get('sales_segment_id'))
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

        if sales_segment_id is not None:
            self.sales_segment = SalesSegment.query \
                .join(SalesSegment.sales_segment_group) \
                .join(SalesSegmentGroup.event) \
                .join(Event.organization) \
                .filter(Organization.id == self.user.organization_id) \
                .filter(SalesSegment.id == sales_segment_id) \
                .one()

            if self.performance is not None and \
               self.sales_segment.performance_id != self.performance.id:
                raise Exception() # XXX
            if self.performance is None:
                self.performance = self.sales_segment.performance
        else:
            self.sales_segment = None

        if point_grant_setting_id is not None:
            self.point_grant_setting = PointGrantSetting.query \
                .filter(Organization.id == self.user.organization_id) \
                .filter(PointGrantSetting.id == point_grant_setting_id) \
                .one()
        else:
            self.point_grant_setting = None

