# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.topic.models import Topic
from altaircms.topcontent.models import Topcontent
from altaircms.widget.models import Widget
from altaircms.lib.interception import not_support_if_keyerror
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from . import renderable
from datetime import datetime
"""
1つのwidgetは１つのトピックを持つ
"""

class TopicWidget(Widget):
    now_date_function = datetime.now

    implements(IWidget)
    type = "topic"

    __tablename__ = "widget_topic"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    topic_type = sa.Column(sa.String(255)) #topiccontent or topic
    display_count = sa.Column(sa.Integer)
    display_global = sa.Column(sa.Boolean)
    display_event = sa.Column(sa.Boolean)
    display_page = sa.Column(sa.Boolean)
    kind = sa.Column(sa.Unicode(255))

    def merge_settings(self, bname, bsettings):
        return getattr(self, self.topic_type+"_merge_settings")(bname, bsettings)

    ## todo: refactoring
    def topcontent_merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")

        @not_support_if_keyerror("topic widget: %(err)s")
        def topcontent_render():
            d = self.now_date_function()
            request = bsettings.extra["request"]
            page = bsettings.extra["page"] if self.display_page else None
            qs = Topcontent.matched_qs(page=page, d=d, kind=self.kind)
            return renderable.render_topcontent(self, qs, self.display_count, self.display_global, request=request)
        bsettings.add(bname, topcontent_render)
        
    def topic_merge_settings(self, bname, bsettings):
        ## jsを追加(一回だけ)
        if not bsettings.is_attached(self, "js_postrender"):
            bsettings.add("js_postrender", TOPIC_JS)
            bsettings.attach_widget(self, "js_postrender")

        ## css追加(1回だけ)
        if not bsettings.is_attached(self, "css_prerender"):
            bsettings.add("css_prerender", TOPIC_CSS)
            bsettings.attach_widget(self, "css_prerender")


        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        bsettings.need_extra_in_scan("event")

        @not_support_if_keyerror("topic widget: %(err)s")
        def topic_render():
            d = self.now_date_function()
            request = bsettings.extra["request"]
            event = bsettings.extra["event"] if self.display_event else None
            page = bsettings.extra["page"] if self.display_page else None
            qs = Topic.matched_qs(page=page, event=event, d=d, kind=self.kind)
            return renderable.render_topics(self, qs, self.display_count, self.display_global, request=request)
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
