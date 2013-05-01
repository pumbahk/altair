# -*- coding:utf-8 -*-
import time
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from .impl import ILayoutModelResolver

import logging
logger = logging.getLogger(__file__)

from ..pyramidlayout import get_subcategories_from_page #obsolete
from .. import pyramidlayout
from altaircms.models import Performance
from altaircms.templatelib.api import refresh_template_cache_only_needs

def get_frontpage_renderer(request):
    """ rendererを取得
    """
    return FrontPageRenderer(request)

def get_frontpage_template_resolver(request):
    return request.registry.getUtility(ILayoutModelResolver)

from pyramid.renderers import RendererHelper    

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
        return self._render(template, page.layout, params)

    def _render(self, template, layout, params):
        return self.render_to_response(template, layout, params, self.request)        

    def render_to_response(self, renderer_name, layout, value, request=None, package=None):
        """render_to_response_with_fresh_template"""
        helper = RendererHelper(name=renderer_name, package=package,
                                registry=request.registry)
        template = helper.renderer.implementation()
        self.refresh_template_if_need(template, layout)
        return helper.render_to_response(value, None, request=request)

    def refresh_template_if_need(self, template, layout):
        if not hasattr(template, "cache"):
            logger.warn("*debug validate template: cache is not found")
            return

        if layout.uploaded_at is None:
            return
        uploaded_at = time.mktime(layout.uploaded_at.timetuple())

        fmt = "*debug validate template: layout.updated_at={0}, template.last_modified={1}"
        logger.warn(fmt.format(uploaded_at ,template.last_modified))
        if uploaded_at > template.last_modified:
            resolver = get_frontpage_template_resolver(self.request)
            refresh_targets = [resolver._resolve(f) for f in layout.dependencies]
            refresh_template_cache_only_needs(template, refresh_targets)

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
