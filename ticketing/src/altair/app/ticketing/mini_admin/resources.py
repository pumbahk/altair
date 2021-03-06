# -*- coding:utf-8 -*-
from altair.app.ticketing.core.models import Performance, Event, Organization
from altair.app.ticketing.lots.models import Lot
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound


class MiniAdminResourceBase(TicketingAdminResource):

    def __init__(self, request):
        super(MiniAdminResourceBase, self).__init__(request)


class MiniAdminEventReportResource(MiniAdminResourceBase):
    def __init__(self, request):
        super(MiniAdminEventReportResource, self).__init__(request)

        self.event_id = self.get_event_id()
        self.event = self.get_event(self.event_id)

    def get_event_id(self):
        """イベントIDの取得"""
        # GETのパラメータからevent_id取得
        try:
            event_id = int(self.request.matchdict.get('event_id', 0))
        except ValueError:
            raise HTTPNotFound()

        return event_id

    def get_event(self, event_id):
        """イベントの取得"""
        # ログインユーザーのORGで制限をつけてイベント抽出
        try:
            slave_session = get_db_session(self.request, name="slave")
            event = slave_session.query(Event).filter(
                Event.id == event_id,
                Event.organization_id == self.user.organization_id
            ).one()
        except (NoResultFound, AttributeError):
            raise HTTPNotFound()

        return event


class MiniAdminPerformanceReportResource(MiniAdminResourceBase):

    def __init__(self, request):
        super(MiniAdminPerformanceReportResource, self).__init__(request)

        self.performance = None
        performance_id = None

        if not self.user:
            return

        try:
            performance_id = long(self.request.matchdict.get('performance_id'))
        except (TypeError, ValueError):
            pass

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

            if self.performance is None:
                raise HTTPNotFound()


class MiniAdminOrderSearchResource(MiniAdminResourceBase):
    def __init__(self, request):
        super(MiniAdminOrderSearchResource, self).__init__(request)


class MiniAdminLotResource(MiniAdminResourceBase):
    def __init__(self, request):
        super(MiniAdminLotResource, self).__init__(request)
        try:
            self.lot_id = long(self.request.matchdict.get('lot_id'))
        except (TypeError, ValueError):
            raise HTTPNotFound

    @reify
    def lot(self):
        return Lot.query.join(Event).filter(Lot.id == self.lot_id,
                                            Event.organization_id == self.organization.id).first()

    def exist_operator_event(self):
        if not self.user.group:
            return False

        event = self.lot.event
        exist_event = [operator_event for operator_event in self.user.group.events if
                       operator_event.id == event.id]

        if not exist_event:
            return False

        return True
