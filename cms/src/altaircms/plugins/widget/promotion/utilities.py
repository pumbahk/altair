# -*- coding:utf-8 -*-
from pyramid.renderers import render
from zope.interface import implementer

from altaircms.plugins.interfaces import IWidgetUtility
from altaircms.plugins.widget.api import DisplayTypeSelectRendering
from .models import PromotionWidget
from .api import get_promotion_manager

def render_tstar_top(request, widget):
    limit = 15
    template_name = "altaircms.plugins.widget:promotion/render.html"
    pm = get_promotion_manager(request)
    info = pm.promotion_info(request, widget.promotion_sheet, limit=limit)
    params = {"show_image": pm.show_image, "info": info}
    return render(template_name, params, request=request)

def render_tstar_category_top(request, widget):
    limit =  4
    template_name = "altaircms.plugins.widget:promotion/category_render.html"
    pm = get_promotion_manager(request)
    info = pm.promotion_info(request, widget.promotion_sheet, limit=limit)
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
