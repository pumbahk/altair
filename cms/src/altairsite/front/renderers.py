# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import RendererHelper    
from zope.interface import Interface, implementer, Attribute
import logging
logger = logging.getLogger(__file__)

from .. import pyramidlayout
from altaircms.widget.tree.proxy import WidgetTreeProxy
from .bsettings import BlockSettings
from altaircms.models import Performance
from ..pyramidlayout import get_subcategories_from_page #obsolete

# -*- coding:utf-8 -*-
import os
import urllib
import logging
logger = logging.getLogger(__name__)
from mako.template import Template
from pyramid.httpexceptions import HTTPNotFound
from datetime import datetime
import threading

class IndividualTemplateLookupAdapter(object):
    def __init__(self, lookup, invalidate_check_fn=None, fetch_fn=None, normalize_fn=None): #xxx:
        self.lookup = lookup
        self.invalidate_check_fn = invalidate_check_fn
        self.fetch_fn = fetch_fn
        self.normalize_fn = normalize_fn
        self._mutex = threading.Lock()

    def __getattr__(self, k):
        return getattr(self.lookup, k)

    def get_template(self, uri):
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            adjusted = uri.replace(':', '$')
            adjusted = self.normalize_fn(adjusted)
            try:
                return self._collection[adjusted]
            except KeyError:
                return self._load(uri, adjusted) #xxx:
        return self.lookup.lookup(uri)

    def _check(self, uri, template):
        if template.filename is None:
            return template
        if self.invalidate_check_fn(template.module._modified_time):
            self._collection.pop(uri, None)
            return self._load(template.filename, uri)
        else:
            return template

    def _load(self, name, uri):
        self._mutex.acquire()
        try:
            try:
                # try returning from collection one
                # more time in case concurrent thread already loaded
                return self._collection[uri]
            except KeyError:
                pass
            try:
                self._collection[uri] = template = self.fetch_fn(self, name, uri)
                return template
            except:
                # if compilation fails etc, ensure
                # template is removed from collection,
                # re-raise
                self._collection.pop(uri, None)
                raise
        finally:
            self._mutex.release()

def invalidate_check_datetime(dt, modified_time): #modified_time is utc
    return modified_time is None or (dt-datetime.fromtimestamp(0)).total_seconds > modified_time

class FetchTemplate(object):
    def __init__(self, prefix):
        self.prefix = prefix
        
    def build_url(self, uri):
        return os.path.join(self.prefix, uri.replace("altaircms:templates/front/layout/", ""))

    def __call__(self, lookup, name, uri, module_filename=None):
        logger.info("name: {name}".format(name=name))
        if not "altaircms:templates/front/layout/" in name:
            return lookup.lookup.get_template(name)
        url = self.build_url(name)
        logger.info("fetching: {url}".format(url=url))
        res = urllib.urlopen(url)
        if res.code != 200:
            import pdb; pdb.set_trace()
            raise HTTPNotFound(res.read())
        string = res.read()
        return Template(
            text=string, 
            lookup=lookup,
            module_filename=module_filename,
            **lookup.template_args)

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
        helper.renderer.lookup = IndividualTemplateLookupAdapter( 
            self.request, 
            helper.renderer.lookup,               
            fetch_fn=FetchTemplate("http://tstar-dev.s3.amazonaws.com/cms-layout-templates/"), 
            invalidate_check_fn=partial(invalidate_check_datetime, layout.updated_at), 
            normalize_fn=normalize)
        return helper.render_to_response(value, None, request=request)

from functools import partial
