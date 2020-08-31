# -*- coding:utf-8 -*-
from altair.app.ticketing.core.models import Performance
from altair.app.ticketing.resources import TicketingAdminResource
from altair.sqlahelper import get_db_session
from pyramid.decorator import reify


class RakutenTvSettingResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target_performance(self):
        slave_session = get_db_session(self.request, name="slave")
        return slave_session.query(Performance).filter_by(id=self.performance_id).first()
