# -*- coding:utf-8 -*-

from altaircms.interfaces import IWidget
from altaircms.plugins.interfaces import IWidgetUtility
import logging
logger = logging.getLogger(__file__)
from zope.interface import implements, implementer
import functools

from pyramid.renderers import render
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.topic.models import Topcontent
from altaircms.widget.models import Widget
from altaircms.plugins.base.interception import not_support_if_keyerror
from altaircms.plugins.base import DBSession
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
from datetime import datetime
from altaircms.tag.api import get_tagmanager
from altaircms.plugins.api import list_from_setting_value

@implementer(IWidgetUtility)
class TopcontentWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
        values = 注目のイベント        
        """
        self.settings = dict(configparser.items(TopcontentWidget.type))
        values = list_from_setting_value(self.settings["values"].decode("utf-8"))
        self.choices = zip(values, values)
        return self

        
class TopcontentWidget(Widget):
    now_date_function = datetime.now
    implements(IWidget)
    type = "topcontent"

    __tablename__ = "widget_topcontent"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    display_type = sa.Column(sa.Unicode(length=255))
    display_count = sa.Column(sa.Integer)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"))
    tag = orm.relationship("TopcontentTag", uselist=False)

    def merge_settings(self, bname, bsettings):
        try:
            merge_settings_function = MERGE_SETTINGS_DISPATH[self.display_type]
            merge_settings_function(self, bname, bsettings)
        except KeyError, e:
            logger.warn(e)
            bsettings.add(bname, u"topcontent widget: topcontent_type=%s tag=%s is not found" % (self.topcontent_type, self.tag))

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

def _merge_settings(template_name, widget, bname, bsettings):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")
    @not_support_if_keyerror("topcontent widget: %(err)s")
    def _render():
        d = widget.now_date_function()
        request = bsettings.extra["request"]
        qs = _qs_search(request, widget, d=d)
        return render(template_name, {"widget": widget, "qs": qs}, request)
    bsettings.add(bname, _render)
       

MERGE_SETTINGS_DISPATH = {
   u"注目のイベント": functools.partial(
        _merge_settings, 
        "altaircms.plugins.widget:topcontent/notable_event_render.html")
    }

class TopcontentWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopcontentWidget
    @property
    def Tag(self):
        return get_tagmanager(self.WidgetClass.type, request=self.request).Tag
    def get_widget(self, widget_id):
        return self._get_or_create(TopcontentWidget, widget_id)
