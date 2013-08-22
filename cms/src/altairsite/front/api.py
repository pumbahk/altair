# -*- coding:utf-8 -*-
from zope.interface import Interface, implementer, Attribute
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

class ILayoutModelRenderer(Interface):
    request = Attribute("request")
    def render(assetspec, page):
        pass

def get_frontpage_renderer(request):
    """ rendererを取得
    """
    return FrontPageRenderer(request)

def get_frontpage_discriptor_resolver(request):
    return request.registry.getUtility(ILayoutModelResolver)

from pyramid.renderers import RendererHelper    

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

@implementer(ILayoutModelResolver)
class FrontPageRenderer(object):
    def __init__(self, request):
        self.request = request
        # self.fetcher = TemplateFetcher(request)
        self.params_collector = RenderingParamsCollector(request)

    def render(self, template, page):
        bsettings = self.params_collector.get_bsettings(page)
        params = self.params_collector.build_render_params(page)
        params.update(page=page, display_blocks=bsettings.blocks)
        return self._render(template, page.layout, params)

    def _render(self, assetspec, layout, params):
        logger.info("-assetspec--%s", assetspec)
        return self.render_to_response(assetspec, layout, params, self.request)        

    def render_to_response(self, renderer_name, layout, value, request=None, package=None):
        """render_to_response_with_fresh_template"""
        helper = RendererHelper(name=renderer_name, 
                                package=package,
                                registry=request.registry, 
                                )
        def normalize(uri):
            if layout.uploaded_at:
                return "{}@{}".format(uri, layout.uploaded_at.strftime("%Y%m%d%H%M"))
            return uri

        ## black magic
        helper.renderer.lookup =IndividualTemplateLookupAdapter( 
            self.request, 
            helper.renderer.lookup,               
            fetch_fn=FetchTemplate("http://tstar-dev.s3.amazonaws.com/cms-layout-templates/"), 
            invalidate_check_fn=partial(invalidate_check_datetime, layout.updated_at), 
            normalize_fn=normalize)
        return helper.render_to_response(value, None, request=request)

from altaircms.templatelib import IndividualTemplateLookupAdapter
from altaircms.templatelib import FetchTemplate
from altaircms.templatelib import invalidate_check_datetime
from functools import partial
