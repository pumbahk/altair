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
    topic = orm.relationship("Topic", backref="widget", uselist=False)

    def merge_settings(self, bname, bsettings):
        ## jsを追加(一回だけ)
        if not bsettings.is_attached(self, "js_postrender"):
            def js():
                return TOPIC_JS
            bsettings.add("js_postrender", js)
            bsettings.attach_widget(self, "js_postrender")

        ## css追加(1回だけ)
        if not bsettings.is_attached(self, "css_prerender"):
            def css():
                return TOPIC_CSS
            bsettings.add("css_prerender", css)
            bsettings.attach_widget(self, "css_prerender")

        bsettings.need_extra_in_scan("request")
        def topic_render():
            request = bsettings.extra["request"]
            return render(self.template_name, {"widget":self, "topic":self.topic}, request)
        bsettings.add(bname, topic_render)

"""
ここに直接jsやcssのコードを埋め込むのはさすがにどうかと思う。
(下のコードがトピックwidgetのtooltipのために必要.(jquerytools必要))
"""
TOPIC_JS = u"""\
// with topic widget
$(".topic").tooltip();
"""

TOPIC_CSS = u"""\
  /* tooltip用のcss (topic widget) */
  .tooltip h2 {
    background-color:#ee8;
  }
  .tooltip {
    display:none;
    background-color:#ffa;
    border:1px solid #cc9;
    padding:3px;
	width: 600px;
    font-size:13px;
    -moz-box-shadow: 2px 2px 11px #666;
    -webkit-box-shadow: 2px 2px 11px #666;
  }
"""
class TopicWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopicWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TopicWidget, widget_id)
