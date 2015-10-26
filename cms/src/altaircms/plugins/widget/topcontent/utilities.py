# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from functools import partial
from altaircms.datelib import get_now
from pyramid.renderers import render
from zope.interface import implementer

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from altaircms.topic.api import get_topic_searcher
from .models import TopcontentWidget

def render_topics_with_template(template_name, request, widget):
    d = get_now(request)
    searcher = get_topic_searcher(request, widget.type)

    qs = searcher.query_publishing_topics(d, widget.tag, widget.system_tag)
    qs = qs.options(orm.joinedload("linked_page"), orm.joinedload("linked_page.event")).limit(widget.display_count)
    qs = [q for q in qs if q.image_asset_id]
    result = render(template_name, {"widget": widget, "qs": qs}, request)
    return result

render_notable_event = partial(render_topics_with_template, "altaircms.plugins.widget:topcontent/notable_event_render.html")
render_soundc_event = partial(render_topics_with_template, "altaircms.plugins.widget:topcontent/soundc_event_render.html")
render_leisure_event = partial(render_topics_with_template, "altaircms.plugins.widget:topcontent/leisure_event_render.html")
@implementer(IWidgetUtility)
class TopcontentWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
utility = altaircms.plugins.widget.topcontent.models.TopcontentWidgetUtilityDefault
names = notable_event
jnames = 注目のイベント        
        """
        self.settings = dict(configparser.items(TopcontentWidget.type))
        self.rendering = DisplayTypeSelectRendering(self.settings, configparser)

        self.rendering.register("notable_event", render_notable_event)
        self.rendering.register("soundc_event", render_soundc_event)
        self.rendering.register("leisure_event", render_leisure_event)

        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type or "default"
        return self.rendering.lookup(display_type, default="")(request, widget)

