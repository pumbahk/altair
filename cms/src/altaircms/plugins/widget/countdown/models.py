# -*- coding:utf-8 -*-

import datetime
from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

import altaircms.helpers as h
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from altaircms.plugins.base.interception import not_support_if_keyerror

from pyramid.renderers import render

class CountdownWidget(Widget):
    implements(IWidget)
    type = "countdown"

    template_name = "altaircms.plugins.widget:countdown/render.mako"
    __tablename__ = "widget_countdown"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.String(25))

    KIND_MAPPING = dict(event_open=u"公演開始", 
                   event_close=u"公演終了", 
                   deal_open=u"販売開始", 
                   deal_close=u"販売終了")
    @property
    def kind_ja(self):
        return self.KIND_MAPPING[self.kind]


    def get_limit(self, event, today_fn=datetime.datetime.now):
        limit_date = getattr(event, self.kind)
        return h.base.countdown_days_from(limit_date, today_fn=today_fn)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("event")

        @not_support_if_keyerror("countdown widget: %(err)s")
        def countdown_render():
            request = bsettings.extra["request"]
            event = bsettings.extra["event"]
            limit = self.get_limit(event)
            return render(self.template_name, {"widget": self, "limit": limit}, request)
        bsettings.add(bname, countdown_render)

class CountdownWidgetResource(HandleSessionMixin,
                                UpdateDataMixin,
                                HandleWidgetMixin,
                                RootFactory
                          ):
    WidgetClass = CountdownWidget

    def get_widget(self, widget_id):
        return self._get_or_create(CountdownWidget, widget_id)
