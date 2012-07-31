# -*- encoding:utf-8 -*-
"""
utility ?
"""
import re
from zope.interface import implementer
from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.api import list_from_setting_value
from .models import CalendarWidget
import logging
logger = logging.getLogger(__file__)

from . import renderable

@implementer(IWidgetUtility)
class CalendarWidgetUtilityDefault(object):
    SPLIT_RX = re.compile("\n")
    def __init__(self):
        self.renderers = None
        self.choices = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
        values = 
          tab
        labels = 
          タブ形式の出力
        renderers =
          altaircms.plugins.widget.calendar:BJ89ers.tab-calendar.mako
        rendering_functions = 
          altaircms.plugins.widget.calendar.rendererable.tab
        """
        self.settings = dict(configparser.items(CalendarWidget.type))
        values = list_from_setting_value(self.settings["values"].decode("utf-8"))
        labels = list_from_setting_value(self.settings["labels"].decode("utf-8"))

        self.choices = zip(values, labels)
        self.renderers = dict(zip(values, list_from_setting_value(self.settings["renderers"])))
        maybe_dotted = config.maybe_dotted
        fns =  [maybe_dotted(x) for x in \
                    list_from_setting_value(self.settings["rendering_functions"])]
        self.rendering_functions = dict(zip(values, fns))
        return self

    def validation(self):
        ## todo rendering dummy object
        return True

    def get_template_name(self, request, widget):
        return self.renderers[widget.calendar_type]

    def get_rendering_function(self, request, widget):
        calendar_type = widget.calendar_type
        return self.rendering_functions.get(calendar_type) or getattr(renderable, calendar_type)
