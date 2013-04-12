# -*- coding:utf-8 -*-
from zope.interface import implementer
from functools import partial
from altaircms.plugins.interfaces import IWidgetUtility
from pyramid.renderers import render
from altaircms.plugins.widget.api import DisplayTypeSelectRendering

from .models import PerformancelistWidget

## todo refactoring
WEEK =[u"月", u"火", u"水", u"木", u"金", u"土", u"日"]
def render_performancelist_with_template(template_name, request,  widget, bsettings):
    """ rendering: title,  iconset,  performance list
    """
    performances = bsettings.extra["performances"]
    performances = list(sorted(performances, key=lambda p: (p.display_order, p.start_on)))
    event = bsettings.extra["event"]
    request = bsettings.extra["request"]
    icon_classes = event.service_info_list
    return render(template_name, 
                  {"performances": performances, 
                   "event": event, 
                   "widget": widget, 
                   "icon_classes": icon_classes, 
                   "WEEK": WEEK}, 
                  request)

render_fullset = partial(render_performancelist_with_template,  "altaircms.plugins.widget:performancelist/render.html")
render_soundc = partial(render_performancelist_with_template,  "altaircms.plugins.widget:performancelist/soundc_render.html")

@implementer(IWidgetUtility)
class PerformancelistWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        self.settings = dict(configparser.items(PerformancelistWidget.type))
        self.rendering = DisplayTypeSelectRendering(self.settings, configparser)
        self.rendering.register("fullset", render_fullset)
        self.rendering.register("soundc", render_soundc)
        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        kind = widget.kind or "default"

        return self.rendering.lookup(kind, default="")(request, widget, bsettings)
