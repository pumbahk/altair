# -*- coding:utf-8 -*-

from zope.interface import implements
from altaircms.interfaces import IWidget
import logging
logger = logging.getLogger(__file__)
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
            merge_settings_function = MERGE_SETTINGS_DISPATH[(self.topcontent_type, self.kind)]
            merge_settings_function(self, bname, bsettings)
        except KeyError, e:
            logger.warn(e)
            bsettings.add(bname, u"topcontent widget: topcontent_type=%s kind=%s is not found" % (self.topcontent_type, self.kind))

def _qs_refine(qs, model, widget):
    if not widget.display_global:
        qs = qs.filter(model.is_global == False)
    if qs.count() > widget.display_count:
        qs = qs.limit(widget.display_count)
    return qs

## todo: refactoring
def topcontents_merge_settings(template_name, widget, bname, bsettings):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")

    @not_support_if_keyerror("topcontent widget: %(err)s")
    def topcontents_render():
        d = widget.now_date_function()
        request = bsettings.extra["request"]
        page = bsettings.extra["page"].pageset if widget.display_page else None
        qs = Topcontent.matched_qs(page=page, d=d, kind=widget.kind, subkind=widget.subkind)
        qs = request.allowable(Topcontent, qs=qs)
        qs = _qs_refine(qs, Topcontent, widget).options(orm.joinedload("linked_page"))
        return render(template_name, 
                      {"widget": widget, "topcontents": qs}, 
                      request)
    bsettings.add(bname, topcontents_render)

def _merge_settings(template_name, widget, bname, bsettings):
    bsettings.need_extra_in_scan("request")
    bsettings.need_extra_in_scan("page")

    @not_support_if_keyerror(" widget: %(err)s")
    def _render():
        d = widget.now_date_function()
        request = bsettings.extra["request"]
        page = bsettings.extra["page"] if widget.display_page else None
        qs = Topcontent.matched_qs(page=page, d=d, kind=widget.kind, subkind=widget.subkind)
        qs = request.allowable(Topcontent, qs=qs)
        qs = _qs_refine(qs, Topcontent, widget)
        qs = qs.options(orm.joinedload("linked_page"),
                        orm.joinedload("linked_page.event"), 
                        orm.joinedload("image_asset"))
        return render(template_name, 
                      {"widget": widget, "s": qs}, 
                      request)
    bsettings.add(bname, _render)
       

MERGE_SETTINGS_DISPATH = {
    ("noimage", u"CR質問"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/CR_faq_render.html"
        ), 
    ("noimage", u"NH質問"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/NH_faq_render.html"
        ), 
    ("noimage", u"89ers質問"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/89ers_faq_render.html"
        ), 
    ("noimage", u"vissel質問"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/vissel_faq_render.html"
        ), 
    ("noimage", u"89ers取引方法詳細"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/89ers_info_render.html"
        ), 
    ("noimage", u"トピックス"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/topcontent_render.html"), 
    ("noimage", u"特集"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/sidebar_feature_render.html"), 
    ("noimage", u"特集(サブカテゴリ)"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/sidebar_category_genre.html"), 
    ("noimage", u"公演中止情報"): functools.partial( ##
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/change_render.html"), 
    ("noimage", u"その他"): functools.partial( ##
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/topcontent_render.html"), 
    ("noimage", u"ヘルプ"): functools.partial(
        topcontents_merge_settings, 
        "altaircms.plugins.widget:topcontent/help_topcontent_render.html"), 
    ("hasimage", u"注目のイベント"): functools.partial(
        _merge_settings, 
        "altaircms.plugins.widget:topcontent/notable_event_render.html")
    }

class TopcontentWidgetResource(HandleSessionMixin,
                          UpdateDataMixin,
                          HandleWidgetMixin,
                          RootFactory
                          ):
    WidgetClass = TopcontentWidget

    def get_widget(self, widget_id):
        return self._get_or_create(TopcontentWidget, widget_id)
