# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from datetime import datetime
from pyramid.renderers import render
from zope.interface import implementer

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from altaircms.tag.api import get_tagmanager
from altaircms.topic.models import Topcontent

from .models import TopcontentWidget

def render_notable_event(request, widget):
    d = datetime.now()
    qs = _qs_search(request, widget, d=d)
    template_name = "altaircms.plugins.widget:topcontent/notable_event_render.html"
    return render(template_name, {"widget": widget, "qs": qs}, request)

## todo: refactoring
def _qs_search(request, widget, d=None):
    tagmanager = get_tagmanager(widget.type, request=request)
    qs = tagmanager.search_by_tag(widget.tag)
    qs = Topcontent.matched_qs(d=d, qs=qs)
    qs = request.allowable(Topcontent, qs=qs)
    if qs.count() > widget.display_count:
        qs = qs.limit(widget.display_count)
    qs = qs.options(orm.joinedload("linked_page"),
                    orm.joinedload("image_asset"))
    return qs

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
        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type or "default"
        return self.rendering.lookup(display_type, default="")(request, widget)

