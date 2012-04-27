# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
import functools

from pyramid.renderers import render
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
    topic_type = sa.Column(sa.String(255), default="topic") #topiccontent or topic
    display_count = sa.Column(sa.Integer)
    display_global = sa.Column(sa.Boolean)
    display_event = sa.Column(sa.Boolean)
    display_page = sa.Column(sa.Boolean)
    kind = sa.Column(sa.Unicode(255))

    def merge_settings(self, bname, bsettings):
        merge_settings_function = MERGE_SETTINGS_DISPATH[self.kind]
        merge_settings_function(self, bname, bsettings)

def _qs_refine(qs, model, widget):
    if not widget.display_global:
        qs = qs.filter(model.is_global == False )
    if qs.count() > widget.display_count:
        qs = qs.limit(widget.display_count)
    return qs

## todo: refactoring
def topics_merge_settings(template_name, widget, bname, bsettings):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")

    @not_support_if_keyerror("topic widget: %(err)s")
    def topics_render():
        d = widget.now_date_function()
        request = bsettings.extra["request"]
        page = bsettings.extra["page"] if widget.display_page else None
        qs = Topic.matched_qs(page=page, d=d, kind=widget.kind)
        qs = _qs_refine(qs, Topic, widget)
        return render(template_name, 
                      {"widget": widget, "topics": qs}, 
                      request)
    bsettings.add(bname, topics_render)

def topcontent_merge_settings(template_name, widget, bname, bsettings):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")

    @not_support_if_keyerror("topcontent widget: %(err)s")
    def topcontent_render():
        d = widget.now_date_function()
        request = bsettings.extra["request"]
        page = bsettings.extra["page"] if widget.display_page else None
        qs = Topcontent.matched_qs(page=page, d=d, kind=widget.kind)
        qs = _qs_refine(qs, Topcontent, widget)
        import pdb; pdb.set_trace()
        return render(template_name, 
                      {"widget": widget, "topcontent": qs}, 
                      request)
    bsettings.add(bname, topcontent_render)
       

MERGE_SETTINGS_DISPATH = {
    u"トピックス": functools.partial(
        topics_merge_settings, 
        "altaircms.plugins.widget:topic/topic_render.mako"), 
    "topcontent": functools.partial(
        topcontent_merge_settings, 
        "altaircms.plugins.widget:topic/topcontent_render.mako")
    }

class TopicWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopicWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TopicWidget, widget_id)

# def topic_merge_settings(widget, bname, bsettings):
#     ## jsを追加(一回だけ)
#     if not bsettings.is_attached(widget, "js_postrender"):
#         bsettings.add("js_postrender", TOPIC_JS)
#         bsettings.attach_widget(widget, "js_postrender")

#     ## css追加(1回だけ)
#     if not bsettings.is_attached(widget, "css_prerender"):
#         bsettings.add("css_prerender", TOPIC_CSS)
#         bsettings.attach_widget(widget, "css_prerender")


#     bsettings.need_extra_in_scan("request")
#     bsettings.need_extra_in_scan("page")
#     bsettings.need_extra_in_scan("event")

#     @not_support_if_keyerror("topic widget: %(err)s")
#     def topic_render():
#         d = widget.now_date_function()
#         request = bsettings.extra["request"]
#         event = bsettings.extra["event"] if widget.display_event else None
#         page = bsettings.extra["page"] if widget.display_page else None
#         qs = Topic.matched_qs(page=page, event=event, d=d, kind=widget.kind)
#         return renderable.render_topics(widget, qs, widget.display_count, widget.display_global, request=request)
#     bsettings.add(bname, topic_render)

# """
# ここに直接jsやcssのコードを埋め込むのはさすがにどうかと思う。
# (下のコードがトピックwidgetのtooltipのために必要.(jquerytools必要))
# """
# TOPIC_JS = u"""\
#   // with topic widget
#   $(".topic").tooltip();
# """

# TOPIC_CSS = u"""\
#   /* tooltip用のcss (topic widget) */
#   .tooltip h2 {
#     background-color:#ee8;
#   }
#   .tooltip {
#     display:none;
#     background-color:#ffa;
#     border:1px solid #cc9;
#     padding:3px;
# 	width: 600px;
#     font-size:13px;
#     -moz-box-shadow: 2px 2px 11px #666;
#     -webkit-box-shadow: 2px 2px 11px #666;
#   }
# """
