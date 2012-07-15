# -*- coding:utf-8 -*-
from datetime import datetime
import sqlalchemy as sa
from pyramid.path import AssetResolver
from pyramid.renderers import render_to_response

from altaircms.tag.models import HotWord
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from . import helpers as h
from .impl import ILayoutTemplateLookUp

from .helpers import get_navigation_categories

import logging
logger = logging.getLogger(__file__)

def get_current_hotwords(request, _nowday=datetime.now):
    today = _nowday()
    qs =  HotWord.query.filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end)
    qs = qs.filter_by(enablep=True).order_by(sa.asc("orderno"), sa.asc("term_end"))
    return qs

def get_frontpage_render(request):
    """ rendererを取得
    """
    return FrontPageRenderer(request)

def get_frontpage_template(request, filename):
    """ layout.modelのfilenameからlayoutファイルのpathを探す
    """
    if filename is None:
        return None
    return request.registry.queryUtility(ILayoutTemplateLookUp)(filename)

def template_exist(template):
    try:
        assetresolver = AssetResolver()
        return assetresolver.resolve(template).exists()
    except Exception, e:
        logger.exception(str(e))
        return False


def is_renderable_template(template, page): ## todo 適切なexception
    if template is None:
        fmt = "*front pc access rendering* page(id=%s) layout(id=%s) don't have template"
        raise Exception( fmt % (page.id, page.layout.id))
    if not template_exist(template):
        fmt = "*front pc access rendering* page(id=%s) layout(id=%s) template(name:%s) is not found"
        raise Exception(fmt % (page.id, page.layout.id, template))
    return True


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
        params = h.get_navigation_categories(self.request)
        params.update(sub_categories=h.get_subcategories_from_page(self.request, page), 
                      myhelper=h)
        return params
