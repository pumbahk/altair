# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from altaircms.datelib import get_now
from collections import namedtuple
from pyramid.renderers import render
from zope.interface import implementer

import altaircms.helpers as h
from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from .models import PromotionWidget
from altaircms.topic.models import Promotion
from altaircms.asset.models import ImageAsset
from .api import get_promotion_manager, get_interval_time
from altaircms.topic.api import get_topic_searcher

## fixme: rename **info
PromotionInfo = namedtuple("PromotionInfo", "idx thumbnails message main width height main_link links messages interval_time unit_candidates")

class PromotionSheet(object):
    def __init__(self, promotion_units):
        self.promotion_units = promotion_units

    def as_info(self, request, idx=0, limit=15):
        ## todo optimize
        punits = self.promotion_units[:limit] if len(self.promotion_units) > limit else self.promotion_units
        if not punits:
            return None

        selected = punits[idx]
        thumbnail_assets_dict = {a.id: a for a in ImageAsset.query.filter(ImageAsset.id.in_([pu.main_image_id for pu in punits])).all()}
        return PromotionInfo(
            thumbnails=[h.asset.rendering_object(request, thumbnail_assets_dict.get(pu.main_image_id)).thumbnail_path for pu in punits], 
            idx=idx, 
            message=selected.text, 
            main=h.asset.rendering_object(request, selected.main_image).filepath, 
            width= selected.main_image.width, 
            height= selected.main_image.height, 
            main_link=h.link.get_link_from_promotion(request, selected), 
            links=[h.link.get_link_from_promotion(request, pu) for pu in punits], 
            messages=[pu.text for pu in punits], 
            interval_time = get_interval_time(), 
            unit_candidates = [int(pu.id) for pu in punits]
            )

def promotion_sheet(request, widget):
    d = get_now(request)
    searcher = get_topic_searcher(request, widget.type)

    qs = searcher.query_publishing_topics(d, widget.tag, widget.system_tag)
    qs = qs.options(orm.joinedload(Promotion.linked_page))
    return PromotionSheet(qs.all()) ##

def render_tstar_top(request, widget):
    limit = 15
    template_name = "altaircms.plugins.widget:promotion/render.html"
    pm = get_promotion_manager(request)
    info = pm.promotion_info(request, promotion_sheet(request, widget), limit=limit)
    params = {"show_image": pm.show_image, "info": info}
    return render(template_name, params, request=request)

def render_tstar_category_top(request, widget):
    limit =  4
    template_name = "altaircms.plugins.widget:promotion/category_render.html"
    pm = get_promotion_manager(request)
    info = pm.promotion_info(request, promotion_sheet(request, widget), limit=limit)
    params = {"show_image": pm.show_image, "info": info}
    return render(template_name, params, request=request)

@implementer(IWidgetUtility)
class PromotionWidgetUtilityDefault(object):
    def __init__(self):
        self.renderers = None
        self.choices = None
        self.status_impl = None

    def parse_settings(self, config, configparser):
        """以下のような形式のものを見る
[promotion]
utility = altaircms.plugins.widget.promotion.models.PromotionWidgetUtilityDefault
jnames =
  チケットスター:Topプロモーション枠
  チケットスター:カテゴリTopプロモーション枠
names = 
  tstar_top

        """
        self.settings = dict(configparser.items(PromotionWidget.type))
        self.rendering = DisplayTypeSelectRendering(self.settings, configparser)

        self.rendering.register("tstar_top", render_tstar_top)
        self.rendering.register("tstar_category_top", render_tstar_category_top)
        self.choices = self.rendering.choices
        return self

    def validation(self):
        return self.rendering.validation()

    def render_action(self, request, page, widget, bsettings):
        display_type = widget.display_type or "default"
        return self.rendering.lookup(display_type, default="tstar_top")(request, widget)
