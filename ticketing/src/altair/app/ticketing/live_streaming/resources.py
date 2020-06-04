# -*- coding:utf-8 -*-
from altair.app.ticketing.resources import TicketingAdminResource
from altair.app.ticketing.core.models import (
    Event, Performance, LivePerformanceSetting
)
from pyramid.decorator import reify
from ..events.printed_reports import api
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound


class LiveStreamingResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id==self.performance_id,
                                        Performance.event_id==Event.id,
                                        Event.organization_id==self.organization.id).first()

    def save_live_streaming_setting(self, form):
        setting = LivePerformanceSetting.query.filter(
            LivePerformanceSetting.performance_id == self.performance_id).first()

        if not setting:
            # 新規作成
            setting = LivePerformanceSetting()
        setting.performance_id = self.performance_id
        setting.label = form.label.data
        setting.live_code = form.live_code.data
        setting.description = form.description.data
        setting.publish_start_at = form.publish_start_at.data
        setting.publish_end_at = form.publish_end_at.data
        setting.save()
