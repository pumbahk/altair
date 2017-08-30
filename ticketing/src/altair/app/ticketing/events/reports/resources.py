# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from altair.sqlahelper import get_db_session
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import Event


class ReportAdminResource(TicketingAdminResource):
    def __init__(self, request):
        super(ReportAdminResource, self).__init__(request)

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
        except NoResultFound:
            raise HTTPNotFound()

        return event
