# -*- coding:utf-8 -*-

import re
from zope.interface import implements
from altaircms.interfaces import IWidget

import sqlalchemy as sa
import sqlalchemy.orm as orm

from altaircms.plugins.base.interception import not_support_if_keyerror
from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.api import list_from_setting_value
from altaircms.plugins.api import get_widget_utility
from zope.interface import implementer

import logging
logger = logging.getLogger(__file__)

@implementer(IWidgetUtility)
class HeadingWidgetUtilityDefault(object):
    SPLIT_RX = re.compile("\n")
    def __init__(self):
        self.settings = None
        self.choices = None
        self.renderers = None

    def parse_settings(self, config, configparser):
        """ how to write a settings:
        values = heading complex_heading
        labels = 見出し 凝った見出し 
        renderers = 
          <h2 id="%%s">%%s</h2>
          <h2 class="すごい見出し" id="%%s">%%s</h2
        """
        self.settings = dict(configparser.items(HeadingWidget.type))
        values = list_from_setting_value(self.settings["values"].decode("utf-8"))
        labels = list_from_setting_value(self.settings["labels"].decode("utf-8"))

        self.choices = zip(values, labels)
        fmts = list_from_setting_value(self.settings["renderers"].replace("%%", "%"), self.SPLIT_RX)
        self.renderers = dict(zip(values, fmts))
        return self

    def validation(self):
        class Dummy(object):
            kind = None
            html_id = -1000
            text = u"this-is-dummy-text"
        for kind, fmt in self.renderers.items():
            Dummy.kind = kind
            try:
                fmt % (Dummy.html_id, Dummy.text)
            except Exception, e:
                logger.exception(str(e))
                raise
        return True

    def render_function(self, widget):
        fmt = self.renderers.get(widget.kind)
        if fmt:
            result = fmt % (widget.html_id, widget.text)
        else:
            result =  u"heading widget: kind=%s is not found" % widget.kind
        return result

class HeadingWidget(Widget):
    implements(IWidget)
    type = "heading"

    __tablename__ = "widget_heading"
    __mapper_args__ = {"polymorphic_identity": type}

    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    kind = sa.Column(sa.Unicode(255))
    text = sa.Column(sa.Unicode(255))

    @property
    def html_id(self):
        return "heading%d" % self.id

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        @not_support_if_keyerror("heading widget: %(err)s")
        def render():
            request = bsettings.extra["request"]
            page = bsettings.extra["page"]
            utility = get_widget_utility(request, page, self.type)
            return utility.render_function(self)
        bsettings.add(bname, render)

class HeadingWidgetResource(HandleSessionMixin,
                            UpdateDataMixin,
                            HandleWidgetMixin,
                            RootFactory
                            ):
    WidgetClass = HeadingWidget

    def get_widget(self, widget_id):
        return self._get_or_create(HeadingWidget, widget_id)
