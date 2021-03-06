# -*- coding:utf-8 -*-

import sqlalchemy as sa
import sqlalchemy.orm as orm
from pyramid.renderers import RendererHelper
from pyramid.decorator import reify
from zope.interface import Interface, implementer, Attribute
from datetime import datetime
import os
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory, Key
import logging
logger = logging.getLogger(__file__)

from mako.template import Template
from pyramid.httpexceptions import HTTPNotFound

from altaircms.cachelib import FileCacheStore, ForAtomic
from altaircms.widget.tree.proxy import WidgetTreeProxy
from altaircms.models import Performance
from .. import pyramidlayout
from ..pyramidlayout import get_subcategories_from_page #obsolete
from .bsettings import BlockSettings

class IInterceptHandler(Interface):
    def need_refresh(last_modified_at):
        """last modified is time.time() -- ust"""

    def load(lookup, master_name, uri):
        """ getting template. -- lookup is wrapped lookup. lookup.lookup is original."""

    def normalize_for_key(master_name):
        """ converting passed uri for key"""

    def need_intercept(master_name):
        """ if true, intercept"""

class ILookupWrapper(Interface):
    lookup = Attribute("original lookup")
    handler = Attribute("strategy object")

    def get_template(uri, template):
        pass

class ILookupWrapperFactory(Interface):
    def __call__(original_lookup, *args, **kwargs):
        pass

@implementer(ILookupWrapperFactory)
class LayoutModelLookupWrapperFactory(object):
    def __init__(self, directory_spec, loader, prefix, sync_trigger_attribute_name):
        self.directory_spec = directory_spec
        self.prefix = prefix.rstrip("/")
        self.loader = loader
        self.sync_trigger_attribute_name = sync_trigger_attribute_name

    def __call__(self, lookup, layout):
        handler = LayoutModelLookupInterceptHandler(
            self.prefix, self.directory_spec, getattr(layout, self.sync_trigger_attribute_name), self.loader)
        return LookupInterceptWrapper(lookup, handler)

class CompositeLoader(object):
    def __init__(self, cache_loader, loader):
        self.cache_loader = cache_loader
        self.loader = loader
        self.queue = []

    def __call__(self, env, name, normalized_key):
        v = self.cache_loader(env, name, normalized_key)
        # logger.info("** cached value: {}, {}".format(v[:20] if v else v, normalized_key))
        if v is not None:
            return v
        logger.warn("loader:%s, normalized_key:%s 's cache is not found", self.cache_loader.__class__.__name__, normalized_key)
        v = self.loader(env, name, normalized_key)
        if v is not None:
            self.cache_loader.create(env, name, normalized_key, v)
        return v

class FileCacheLoader(object):
    def __init__(self, kwargs, atomic_kwargs):
        self.cache = FileCacheStore(kwargs)
        self.atomic = ForAtomic(atomic_kwargs)

    def create(self, env, name, normalized_key, v):
        # logger.info("*****store data {}".format(normalized_key))
        with self.atomic.atomic(normalized_key):
            self.cache.set(normalized_key, v)

    def __call__(self, env, name, normalized_key):
        status = self.atomic.is_requesting(normalized_key)
        # logger.info("** requesting: {}, {}".format(status, normalized_key))
        if status:
            return None
        with self.atomic.atomic(normalized_key):
            # logger.info("** get from cache. {}".format(normalized_key))
            return self.cache.get(normalized_key)

class S3Loader(object):
    def __init__(self, bucket_name, access_key, secret_key):
        self.connection_factory = DefaultS3ConnectionFactory(access_key, secret_key)
        self.bucket_name = bucket_name

    @reify
    def connection(self):
        return self.connection_factory()

    @reify
    def bucket(self):
        return self.connection.get_bucket(self.bucket_name)

    def __call__(self, env, name, normalized_key):
        logger.info("** S3: get layout template: {}".format(normalized_key))
        uri = env.build_url(name) #xxx:
        k = Key(self.bucket)
        k.key = uri
        return k.get_contents_as_string()


@implementer(IInterceptHandler)
class LayoutModelLookupInterceptHandler(object):
    def __init__(self, prefix, layout_spec, uploaded_at, loader):
        self.prefix = prefix
        self.layout_spec = layout_spec
        self.uploaded_at = uploaded_at
        self.loader = loader 

    def need_intercept(self, uri):
        return self.layout_spec in uri and self.uploaded_at

    def need_refresh(self, last_modified_at):
        return last_modified_at and self.uploaded_at and self.uploaded_at_as_time > last_modified_at

    def normalize_for_key(self, uri):
        adjusted = uri.replace(':', '$') ## pyramid.mako_templating replacing : -> $, temporary, so.
        if self.uploaded_at:
            return "{}@{}".format(adjusted, self.uploaded_at_as_string)
        return adjusted

    def load_template(self, lookup, name, normalized_key, module_filename=None):
        try:
            logger.info("load template -- normalized_key: {normalized_key}".format(normalized_key=normalized_key))
            string = self.loader(self, name, normalized_key)
            return Template(
                text=string, 
                lookup=lookup,
                module_filename=module_filename,
                **lookup.template_args)
        except Exception as e:
            logger.error(e)
            raise HTTPNotFound()

    def build_url(self, uri):
        return "{prefix}/{uri}".format(prefix=self.prefix, uri=uri.replace(self.layout_spec, "").lstrip("/"))

    @reify
    def uploaded_at_as_time(self):
        return (self.uploaded_at-datetime.fromtimestamp(0)).total_seconds()

    @reify
    def uploaded_at_as_string(self):
        return self.uploaded_at.strftime("%Y%m%d%H%M%S")

@implementer(ILookupWrapper)
class LookupInterceptWrapper(object):
    def __init__(self, lookup, handler): #xxx:
        self.lookup = lookup
        self.handler = handler
        # self._mutex = threading.Lock()

    def __getattr__(self, k):
        return getattr(self.lookup, k)

    def get_template(self, uri):
        if not self.handler.need_intercept(uri):
            return self.lookup.get_template(uri)
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            adjusted = self.handler.normalize_for_key(uri)
            try:
                if self.filesystem_checks:
                    return self._check(adjusted, self._collection[adjusted])
                else:
                    return self._collection[adjusted]
            except KeyError:
                return self._load(uri, adjusted) #xxx:
        return self.lookup.get_template(uri)

    def _check(self, uri, template):
        logger.info("checking: template {}".format(template))
        if template.filename is None:
            return template
        if self.handler.need_refresh(template.last_modified): #modified_time is utc
            self._collection.pop(uri, None)
            return self._load(template.filename, uri)
        else:
            return template

    def _load(self, uri, adjusted):
        self._mutex.acquire()
        try:
            try:
                # try returning from collection one
                # more time in case concurrent thread already loaded
                return self._collection[uri]
            except KeyError:
                pass
            try:
                self._collection[adjusted] = template = self.handler.load_template(self, uri, adjusted)
                return template
            except:
                # if compilation fails etc, ensure
                # template is removed from collection,
                # re-raise
                self._collection.pop(uri, None)
                raise
        finally:
            self._mutex.release()

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

    @reify
    def params_collector(self):
        return RenderingParamsCollector(self.request)

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
        ## black magic
        factory = self.request.registry.queryUtility(ILookupWrapperFactory)
        if factory:
            logger.debug("lookup wrapper factory found")
            helper.renderer.lookup = factory(helper.renderer.lookup, layout)
        ###
        return helper.render_to_response(value, None, request=request)
