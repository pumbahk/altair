from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import ReportSetting, Performance, Event, Organization


class SalesReportAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(SalesReportAdminResource, self).__init__(request)

        event_id = None
        performance_id = None

        if not self.user:
            return

        try:
            event_id = long(self.request.matchdict.get('event_id'))
        except (TypeError, ValueError):
            pass

        try:
            performance_id = long(self.request.matchdict.get('performance_id'))
        except (TypeError, ValueError):
            pass

        if event_id is not None:
            try:
                self.event = Event.query \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(Event.id == event_id) \
                    .one()
            except NoResultFound:
                raise HTTPNotFound()
        else:
            self.event = None

        if performance_id is not None:
            try:
                self.performance = Performance.query \
                    .join(Performance.event) \
                    .join(Event.organization) \
                    .filter(Organization.id == self.user.organization_id) \
                    .filter(Performance.id == performance_id) \
                    .one()
            except NoResultFound:
                self.performance = None

            if self.performance is None or \
               (self.event is not None and self.performance.event_id != self.event.id):
                raise HTTPNotFound()
            if self.event is None:
                self.event = self.performance.event
        else:
            self.performance = None


class ReportSettingAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(ReportSettingAdminResource, self).__init__(request)

        report_setting_id = None

        if not self.user:
            return

        try:
            report_setting_id = long(self.request.matchdict.get('report_setting_id'))
        except (TypeError, ValueError):
            pass

        if report_setting_id is not None:
            try:
                self.report_setting = ReportSetting.query.filter_by(id=report_setting_id).one()
            except NoResultFound:
                self.report_setting = None

            if self.report_setting is None or \
               (self.report_setting.event is not None and self.report_setting.event.organization_id != self.user.organization_id) or \
               (self.report_setting.performance is not None and self.report_setting.performance.event.organization_id != self.user.organization_id):
                raise HTTPNotFound()
        else:
            self.report_setting = None
