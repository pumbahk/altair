# -*- coding:utf-8 -*-
import json
from zope.interface import implementer
from altaircms.plugins.interfaces import IWidgetUtility
from pyramid.renderers import render
from .models import SummaryWidget

@implementer(IWidgetUtility)
class SummaryWidgetUtilityDefault(object):
    template_name_default = "altaircms.plugins.widget:summary/render.html"
    def __init__(self):
        self.rendering_template = None

    def parse_settings(self, config, configparser):
        self.settings = dict(configparser.items(SummaryWidget.type))
        self.rendering_template = self.settings["rendering_template"]
        return self

    def render_action(self, request, page, widget, bsettings):
        items = json.loads(widget.items or "[]")
        rendering_template = self.rendering_template or self.template_name_default
        return render(rendering_template, {"widget": widget,  "items": items},  request=request) 
