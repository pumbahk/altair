# -*- coding:utf-8 -*-
import time
import sqlalchemy as sa
import sqlalchemy.orm as orm
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from .resolver import ILayoutModelResolver

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

def get_frontpage_discriptor_resolver(request):
    return request.registry.getUtility(ILayoutModelResolver)

from pyramid.renderers import RendererHelper    

class Lock(object):
    """todo: implementation. we needs filesystem based lock. (not thread local and not dblock(too-wide))"""
    def acquire(self):
        pass

    def release(self):
        pass

_Lock  = Lock()

class TemplateFetcher(object):
    def __init__(self, request):
        self.request = request

    def refresh_template_if_need(self, template, layout):
        if not hasattr(template, "cache"):
            logger.info("*debug validate template: cache is not found")
            return

        if layout.synced_at is None:
            return
        synced_at = time.mktime(layout.synced_at.timetuple())

        fmt = "*debug validate template: layout.updated_at={0}, template.last_modified={1}"
        logger.warn(fmt.format(synced_at ,template.last_modified))
        if synced_at > template.last_modified:
            self.refresh_template_cache(template, layout, synced_at)

    def _refresh_template_cache(self, template, layout, synced_at):
        resolver = get_frontpage_discriptor_resolver(self.request)
        refresh_targets = [resolver.from_assetspec(self.request, f) for f in layout.dependencies]
        refresh_template_cache_only_needs(template, refresh_targets, synced_at)

    def refresh_template_cache(self, template, layout, synced_at):
        _Lock.acquire()
        try:
            self._refresh_template_cache(template, layout, synced_at)
        except:
            _Lock.release()
            raise
        else:
            _Lock.release()

class RenderingParamsCollector(object):
    def __init__(self, request):
        self.request = request

    def get_bsettings(self, page):
        bsettings = BlockSettings.from_widget_tree(WidgetTreeProxy(page))
        bsettings.blocks["description"] = [page.description]
        bsettings.blocks["keywords"] = [page.keywords]
        bsettings.blocks["title"] = [page.title]

        event = page.event
        if event is None:
            performances = []
        else:
            performances = Performance.query.filter(Performance.event_id==event.id, Performance.public==True)
            performances = performances.order_by(sa.asc(Performance.start_on)).options(orm.joinedload("sales")).all()
        ## 本当はwidget側からpullしていくようにしたい
        bsettings.scan(self.request, page=page, performances=performances, event=event)
        return bsettings

    def build_render_params(self, page):
        params = {}
        params.update(sub_categories=get_subcategories_from_page(self.request, page), 
                      myhelper=pyramidlayout)
        return params

class FrontPageRenderer(object):
    def __init__(self, request):
        self.request = request
        self.fetcher = TemplateFetcher(request)
        self.params_collector = RenderingParamsCollector(request)

    def render(self, template, page):
        bsettings = self.params_collector.get_bsettings(page)
        params = self.params_collector.build_render_params(page)
        params.update(page=page, display_blocks=bsettings.blocks)
        return self._render(template, page.layout, params)

    def _render(self, template, layout, params):
        return self.render_to_response(template, layout, params, self.request)        

    def render_to_response(self, renderer_name, layout, value, request=None, package=None):
        """render_to_response_with_fresh_template"""
        helper = RendererHelper(name=renderer_name, package=package,
                                registry=request.registry)
        template = helper.renderer.implementation()
        self.fetcher.refresh_template_if_need(template, layout)
        return helper.render_to_response(value, None, request=request)
