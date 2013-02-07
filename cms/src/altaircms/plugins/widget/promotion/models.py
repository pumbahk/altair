# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from zope.interface import implements, implementer
from altaircms.interfaces import IWidget
from altaircms.plugins.interfaces import IWidgetUtility
from collections import namedtuple
import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import render

from altaircms.widget.models import Widget
from altaircms.plugins.base import DBSession
from altaircms.plugins.api import list_from_setting_value
from altaircms.plugins.base.mixins import HandleSessionMixin
from altaircms.plugins.base.mixins import HandleWidgetMixin
from altaircms.plugins.base.mixins import UpdateDataMixin
from altaircms.security import RootFactory
import altaircms.helpers as h
from altaircms.topic.models import PromotionTag
from altaircms.topic.models import Promotion
from altaircms.plugins.api import get_widget_utility

class PromotionWidget(Widget):
    implements(IWidget)
    type = "promotion"

    __tablename__ = "widget_promotion"
    __mapper_args__ = {"polymorphic_identity": type}
    query = DBSession.query_property()

    id = sa.Column(sa.Integer, sa.ForeignKey("widget.id"), primary_key=True)
    display_type = sa.Column(sa.Unicode(length=255))
    tag_id = sa.Column(sa.Integer, sa.ForeignKey("topiccoretag.id"))
    tag = orm.relationship("PromotionTag", uselist=False)

    @property
    def promotion_sheet(self, d=None):
        from altaircms.topic.models import Promotion
        qs = Promotion.matched_qs(d=d, tag=self.tag.label).options(orm.joinedload("main_image"), orm.joinedload("linked_page"))
        return PromotionSheet(qs.all()) ##

    def merge_settings(self, bname, bsettings):
        bsettings.need_extra_in_scan("request")
        bsettings.need_extra_in_scan("page")
        def closure():
            try:
                request = bsettings.extra["request"]
                page = bsettings.extra["page"]
                utility = get_widget_utility(request, page, self.type)
                return utility.render_action(request, page, self, bsettings)
            except Exception, e:
                logger.exception(str(e))
                logger.warn("promotion_merge_settings. info is empty")
                return u''
        bsettings.add(bname, closure)

@implementer(IWidgetUtility)
class PromotionWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
        values = 
        """
        self.settings = dict(configparser.items(PromotionWidget.type))
        jnames = list_from_setting_value(self.settings["jnames"].decode("utf-8"))
        names = list_from_setting_value(self.settings["names"].decode("utf-8"))
        self.choices = zip(names, jnames)

        self.name_to_jname = dict(self.choices)
        self.jname_to_name = dict(zip(jnames, names))
        return self

    def validation(self):
        for name, _ in self.choices:
            getattr(self, "render_action_%s" % name)
        return True

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type
        k = self.name_to_jname.get(display_type, "default")
        return getattr(self, "render_action_%s" % k)(request, widget)

    def render_action_default(self, request, widget):
        return self.render_action_tstar_top(request, widget)

    def render_action_tstar_top(self, request, widget):
        limit = 15
        template_name = "altaircms.plugins.widget:promotion/render.html"
        from . import api
        pm = api.get_promotion_manager(request)
        info = pm.promotion_info(request, widget.promotion_sheet, limit=limit)
        params = {"show_image": pm.show_image, "info": info}
        return render(template_name, params, request=request)

    def render_action_tstar_category_top(self, request, widget):
        limit =  4
        template_name = "altaircms.plugins.widget:promotion/category_render.html"
        from . import api
        pm = api.get_promotion_manager(request)
        info = pm.promotion_info(request, widget.promotion_sheet, limit=limit)
        params = {"show_image": pm.show_image, "info": info}
        return render(template_name, params, request=request)


## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumbnails message main main_link links messages interval_time unit_candidates")

class PromotionSheet(object):
    INTERVAL_TIME = 5000

    def __init__(self, promotion_units):
        self.promotion_units = promotion_units

    def as_info(self, request, idx=0, limit=15):
        ## todo optimize
        punits = self.promotion_units[:limit] if len(self.promotion_units) > limit else self.promotion_units
        if not punits:
            return None

        selected = punits[idx]
        return PromotionInfo(
            thumbnails=[h.asset.to_show_page(request, pu.main_image, filepath=pu.main_image.thumbnail_path) for pu in punits], 
            idx=idx, 
            message=selected.text, 
            main=h.asset.to_show_page(request, selected.main_image), 
            main_link=h.link.get_link_from_promotion(request, selected), 
            links=[h.link.get_link_from_promotion(request, pu) for pu in punits], 
            messages=[pu.text for pu in punits], 
            interval_time = self.INTERVAL_TIME, 
            unit_candidates = [int(pu.id) for pu in punits]
            )

class PromotionWidgetResource(HandleSessionMixin,
                              UpdateDataMixin,
                              HandleWidgetMixin,
                              RootFactory
                              ):
    Promotion = Promotion
    WidgetClass = PromotionWidget
    Tag = PromotionTag
    def get_widget(self, widget_id):
        return self._get_or_create(PromotionWidget, widget_id)
