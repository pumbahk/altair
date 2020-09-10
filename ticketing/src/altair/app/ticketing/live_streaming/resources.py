# -*- coding:utf-8 -*-
from altair.app.ticketing.core.models import (
    Event, Performance, LivePerformanceSetting
)
from altair.app.ticketing.resources import TicketingAdminResource
from pyramid.decorator import reify

from forms import LiveStreamingForm


class LiveStreamingResource(TicketingAdminResource):
    @property
    def performance_id(self):
        return self.request.matchdict["performance_id"]

    @reify
    def target(self):
        return Performance.query.filter(Performance.id == self.performance_id,
                                        Performance.event_id == Event.id,
                                        Event.organization_id == self.organization.id).first()

    @reify
    def live_streaming_setting(self):
        return self.target.live_performance_setting

    def create_form(self):
        form = LiveStreamingForm()

        setting = self.live_streaming_setting
        if setting:
            form.public_flag.data = setting.public_flag
            form.template_type.data = setting.template_type
            form.label.data = setting.label
            form.artist_page.data = setting.artist_page
            form.live_code.data = setting.live_code
            form.live_chat_code.data = setting.live_chat_code
            form.description.data = setting.description
            form.publish_start_at.data = setting.publish_start_at
            form.publish_end_at.data = setting.publish_end_at
        return form

    def save_live_streaming_setting(self, form):
        setting = LivePerformanceSetting.query.filter(
            LivePerformanceSetting.performance_id == self.performance_id).first()

        if not setting:
            # 新規作成
            setting = LivePerformanceSetting()
        setting.performance_id = self.performance_id
        setting.public_flag = form.public_flag.data
        setting.template_type = form.template_type.data
        setting.label = form.label.data
        setting.artist_page = form.artist_page.data
        setting.live_code = form.live_code.data
        setting.live_chat_code = form.live_chat_code.data
        setting.description = form.description.data
        setting.publish_start_at = form.publish_start_at.data
        setting.publish_end_at = form.publish_end_at.data
        setting.save()
