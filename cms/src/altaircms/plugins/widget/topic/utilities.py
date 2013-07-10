# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from functools import partial
from altaircms.datelib import get_now
from pyramid.renderers import render
from zope.interface import implementer

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from altaircms.topic.api import get_topic_searcher

from .models import TopicWidget


def render_topics_with_template(template_name, request, widget):
    d = get_now(request)
    searcher = get_topic_searcher(request, widget.type)

    qs = searcher.query_publishing_topics(d, widget.tag, widget.system_tag)
    qs = qs.options(orm.joinedload("linked_page")).limit(widget.display_count)
    result = render(template_name, {"widget": widget, "topics": qs}, request)
    return result

## todo: refactoring

render_cr_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/CR_faq_render.html")
render_soundc_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/soundc_faq_render.html")
render_nh_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/NH_faq_render.html")
render_89ers_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/89ers_faq_render.html")
render_89ers_info_render = partial(render_topics_with_template, "altaircms.plugins.widget:topic/89ers_info_render.html")
render_vissel_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/vissel_faq_render.html")

render_tstar_topics_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/topic_render.html")
render_tstar_information_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/information_render.html")
render_tstar_feature_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/sidebar_feature_render.html")
render_tstar_genre_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/sidebar_category_genre_render.html")
render_tstar_change_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/change_render.html")
render_tstar_other_faq = partial(render_topics_with_template, "altaircms.plugins.widget:topic/topic_render.html")

## todo 分解
@implementer(IWidgetUtility)
class TopicWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
utility = altaircms.plugins.widget.topic.models.TopicWidgetUtilityDefault
names = notable_event
jnames = 注目のイベント        
        """
        self.settings = dict(configparser.items(TopicWidget.type))
        self.rendering = DisplayTypeSelectRendering(self.settings, configparser)
        self.rendering.register("soundc_faq", render_soundc_faq)
        self.rendering.register("cr_faq", render_cr_faq)
        self.rendering.register("nh_faq", render_nh_faq)
        self.rendering.register("89ers_faq", render_89ers_faq)
        self.rendering.register("89ers_info", render_89ers_info_render)
        self.rendering.register("vissel_faq", render_vissel_faq)
        ## xxx:
        self.rendering.register("faq", render_89ers_faq)

        self.rendering.register("topic", render_tstar_topics_faq)
        self.rendering.register("information", render_tstar_information_faq)
        self.rendering.register("feature", render_tstar_feature_faq)
        self.rendering.register("genre", render_tstar_genre_faq)
        self.rendering.register("change", render_tstar_change_faq)
        self.rendering.register("other", render_tstar_other_faq)

        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type or "default"
        return self.rendering.lookup(display_type, default="")(request, widget)
