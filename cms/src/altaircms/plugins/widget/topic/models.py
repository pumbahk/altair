# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from pyramid.renderers import render

"""
1つのwidgetは１つのトピックを持つ
"""

class TopicWidget(Widget):
    implements(IWidget)
    type = "topic"

    template_name = "altaircms.plugins.widget:topic/render.mako"
    __tablename__ = "widget_topic"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    topic_id = sa.Column(sa.Integer, sa.ForeignKey("topic.id"))
    topic = orm.relationship("Topic", backref="widget", uselist=True)

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        def topic_render():
            request = bsettings.extra["request"]
            return render(self.template_name, {"page":page, "widget":self, "topic":self.topic}, request)
        bsettings.add(bname, topic_render)

class TopicWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopicWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TopicWidget, widget_id)
