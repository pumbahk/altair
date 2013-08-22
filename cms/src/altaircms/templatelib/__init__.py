# -*- coding:utf-8 -*-
import os
import urllib
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from mako.template import Template
from pyramid.httpexceptions import HTTPNotFound
from pyramid.interfaces import (
    ITemplateRenderer, 
    )
from pyramid.settings import asbool
from pyramid.compat import (
    is_nonstr_iter,
    )
from pyramid.mako_templating import (
    IMakoLookup, 
    MakoRendererFactoryHelper, 
    MakoLookupTemplateRenderer, 
    PkgResourceTemplateLookup
    )
from pyramid.util import DottedNameResolver
from datetime import datetime
import threading

class IndividualTemplateLookupAdapter(object):
    def __init__(self, request, lookup, invalidate_check_fn=None, fetch_fn=None, normalize_fn=None): #xxx:
        self.request = request
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
                # if self.filesystem_checks:
                #     return self._check(adjusted, self._collection[adjusted])
                # else:
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

@implementer(ITemplateRenderer)
class FlexibleMakoLookupTemplateRenderer(MakoLookupTemplateRenderer): #TODO:rename
    def wrap_lookup(self, wrapper):
        self.lookup = wrapper(self.lookup)

registry_lock = threading.Lock()

class FlexibleMakoRendererFactoryHelper(object): 
    """almost copy from pyramid.mako_templating.MakoRendererFactoryHelper"""

    def __init__(self, settings_prefix=None, renderer_impl=FlexibleMakoLookupTemplateRenderer):
        self.settings_prefix = settings_prefix
        self.renderer_impl = renderer_impl

    def __call__(self, info):
        path = info.name
        registry = info.registry
        settings = info.settings
        settings_prefix = self.settings_prefix

        if settings_prefix is None:
            settings_prefix = info.type +'.'

        lookup = registry.queryUtility(IMakoLookup, name=settings_prefix)

        def sget(name, default=None):
            return settings.get(settings_prefix + name, default)

        if lookup is None:
            reload_templates = True
            directories = []
            module_directory = None
            input_encoding = sget('input_encoding', 'utf-8')
            error_handler = sget('error_handler', None)
            default_filters = sget('default_filters', 'h')
            imports = sget('imports', None)
            strict_undefined = asbool(sget('strict_undefined', False))
            preprocessor = sget('preprocessor', None)
            if error_handler is not None:
                dotted = DottedNameResolver(info.package)
                error_handler = dotted.maybe_resolve(error_handler)
            if default_filters is not None:
                if not is_nonstr_iter(default_filters):
                    default_filters = list(filter(
                        None, default_filters.splitlines()))
            if imports is not None:
                if not is_nonstr_iter(imports):
                    imports = list(filter(None, imports.splitlines()))
            if preprocessor is not None:
                dotted = DottedNameResolver(info.package)
                preprocessor = dotted.maybe_resolve(preprocessor)

            lookup = PkgResourceTemplateLookup(
                directories=directories,
                module_directory=module_directory,
                input_encoding=input_encoding,
                error_handler=error_handler,
                default_filters=default_filters,
                imports=imports,
                filesystem_checks=reload_templates,
                strict_undefined=strict_undefined,
                preprocessor=preprocessor
                )

            registry_lock.acquire()
            try:
                registry.registerUtility(lookup, IMakoLookup,
                                         name=settings_prefix)
            finally:
                registry_lock.release()
        return self.renderer_impl(path, lookup)

renderer_factory = FlexibleMakoRendererFactoryHelper('s3mako.')

def includeme(config):
    config.add_renderer(".s3mako", renderer_factory)
