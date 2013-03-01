# -*- coding:utf-8 -*-
from datetime import datetime
import sqlalchemy as sa
from pyramid.renderers import render_to_response

from altaircms.tag.models import HotWord
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from . import helpers as h
from .impl import ILayoutTemplateLookUp

import logging
logger = logging.getLogger(__file__)

def get_navigation_categories(request):
    """ ページヘッダのナビゲーション用のcategoryを取得する。
    """
    top_outer_categories = h._get_categories(request, hierarchy=u"top_outer")
    top_inner_categories = h._get_categories(request, hierarchy=u"top_inner")

    categories = h._get_categories(request, hierarchy=u"大")

    return dict(categories=categories,
                top_outer_categories=top_outer_categories,
                top_inner_categories=top_inner_categories)

def get_current_hotwords(request, _nowday=datetime.now):
    today = _nowday()
    qs =  HotWord.query.filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end)
    qs = qs.filter_by(enablep=True).order_by(sa.asc("display_order"), sa.asc("term_end"))
    return qs

def get_frontpage_renderer(request):
    """ rendererを取得
    """
    return FrontPageRenderer(request)

def get_frontpage_template_lookup(request):
    return request.registry.getUtility(ILayoutTemplateLookUp)


"""
todo: 複数の種類に分ける?
"""
class FrontPageRenderer(object):
    def __init__(self, request):
        self.request = request

    def render(self, template, page):
        bsettings = self.get_bsettings(page)
        params = self.build_render_params(page)
        params.update(page=page, display_blocks=bsettings.blocks)
        return render_to_response(template, params, self.request)

    def get_bsettings(self, page):
        bsettings = BlockSettings.from_widget_tree(WidgetTreeProxy(page))
        bsettings.blocks["description"] = [page.description]
        bsettings.blocks["keywords"] = [page.keywords]
        bsettings.blocks["title"] = [page.title]

        event = page.event
        performances=h.get_performances(event)
        ## 本当はwidget側からpullしていくようにしたい
        bsettings.scan(self.request, page=page, performances=performances, event=event)
        return bsettings

    def build_render_params(self, page):
        params = {}
        params.update(sub_categories=h.get_subcategories_from_page(self.request, page), 
                      myhelper=h)
        return params
