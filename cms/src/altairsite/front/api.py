# -*- coding:utf-8 -*-
import sqlalchemy as sa
from pyramid.renderers import render_to_response
import sqlalchemy.orm as orm
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from .impl import ILayoutTemplateLookUp

import logging
logger = logging.getLogger(__file__)

from ..pyramidlayout import get_subcategories_from_page #obsolete
from .. import pyramidlayout
from altaircms.models import Performance

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
        if event is None:
            performances = []
        else:
            performances = Performance.query.filter(Performance.event_id==event.id).order_by(sa.asc(Performance.start_on)).options(orm.joinedload("sales")).all()
        ## 本当はwidget側からpullしていくようにしたい
        bsettings.scan(self.request, page=page, performances=performances, event=event)
        return bsettings

    def build_render_params(self, page):
        params = {}
        params.update(sub_categories=get_subcategories_from_page(self.request, page), 
                      myhelper=pyramidlayout)
        return params
