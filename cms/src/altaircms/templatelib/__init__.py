# -*- coding:utf-8 -*-
import os
import urllib
import shutil

from pyramid.settings import asbool
from mako import exceptions
from pyramid.compat import is_nonstr_iter
from pyramid.util import DottedNameResolver
from pyramid.mako_templating import (
    MakoRendererFactoryHelper, 
    registry_lock, 
    PkgResourceTemplateLookup, 
    IMakoLookup
)
from pyramid.asset import (
    resolve_asset_spec,
    abspath_from_asset_spec,
)
from pyramid.path import AssetResolver
import logging
logger = logging.getLogger()
from zope.interface import implementer
from zope.interface import Interface

class IMakoLookupFactory(Interface):
    def __call__(*args, **kwargs):
        pass

class IFailbackLookup(Interface):
    def __call__(lookup, uri):
        """return template"""

#utility
def get_renderer_factory(request, filename):
    from pyramid.interfaces import IRendererFactory
    ext = os.path.splitext(filename)[1]
    return request.registry.queryUtility(IRendererFactory, name=ext)


@implementer(IMakoLookup)
class HasFailbackTemplateLookup(PkgResourceTemplateLookup):
    def __init__(self, failback_lookup, *args, **kwargs):
        self.failback_lookup = failback_lookup
        super(HasFailbackTemplateLookup, self).__init__(*args, **kwargs)

    def get_template_failback(self, uri): #need cache
        return self.failback_lookup(self, uri)

    def get_template(self, uri):
        try:
            return super(HasFailbackTemplateLookup, self).get_template(uri)
        except exceptions.TopLevelLookupException as e:
            try:
                v = self.get_template_failback(uri)
                if v:
                    return v
                raise e
            except Exception as sube:
                logger.exception(sube)
                raise e

@implementer(IFailbackLookup)
class DefaultFailbackLookup(object):
    def __init__(self, host, assetspec):
        self.host = host.rstrip("/")
        self.assetspec = assetspec
        self.default_directory = AssetResolver().resolve(assetspec).abspath()        
        if not ":" in assetspec:
            self.prefix = assetspec+":"
        else:
            self.prefix = assetspec.rstrip("/")+"/"    

    @classmethod 
    def from_settings(cls, settings, prefix=""):
        return cls(settings[prefix+"lookup.host"], 
                   settings.get(prefix+"directories", [None])[0])

    def is_assetspec(self, uri):
        return ":" in uri

    def __call__(self, lookup, uri):
        if not self.is_assetspec(uri):
            uri = "{0}{1}".format(self.prefix, uri)
        lookup_url = "{0}/{1}".format(self.host, uri.lstrip("/"))
        res = urllib.urlopen(lookup_url)
        if res.getcode() != 200:
            return None
        adjusted = uri.replace(':', '$')
        pname, path = resolve_asset_spec(uri)
        srcfile = abspath_from_asset_spec(path, pname)
        try:
            with open(srcfile, "wb") as wf:
                shutil.copyfileobj(res, wf)
        except IOError:
            os.makedirs(os.path.dirname(srcfile).rstrip(".."))
            with open(srcfile, "wb") as wf:
                shutil.copyfileobj(res, wf)
        return lookup._load(srcfile, adjusted)

@implementer(IMakoLookupFactory)
class HasFailbackTemplateLookupFactory(object):
    TemplateLookupClass = HasFailbackTemplateLookup
    def __init__(self, failback_lookup, name):
        self.failback_lookup = failback_lookup
        self.name = name

    def __call__(self, *args, **kwargs):
        return self.TemplateLookupClass(
            self.failback_lookup,
            *args, **kwargs)

_settings_prefix = "s3.mako."

# almost copy of mako_templating.
def _make_lookup(config, package=None, _settings_prefix=_settings_prefix):
    settings = config.registry.settings
    def sget(name, default=None):
        return settings.get(_settings_prefix + name, default)
    reload_templates = settings.get('pyramid.reload_templates', None)
    if reload_templates is None:
        reload_templates = settings.get('reload_templates', False)
    reload_templates = asbool(reload_templates)
    directories = sget('directories', [])
    module_directory = sget('module_directory', None)
    input_encoding = sget('input_encoding', 'utf-8')
    error_handler = sget('error_handler', None)
    default_filters = sget('default_filters', 'h')
    imports = sget('imports', None)
    strict_undefined = asbool(sget('strict_undefined', False))
    preprocessor = sget('preprocessor', None)
    if not is_nonstr_iter(directories):
        directories = list(filter(None, directories.splitlines()))
    directories = [ abspath_from_asset_spec(d) for d in directories ]
    if module_directory is not None:
        module_directory = abspath_from_asset_spec(module_directory)
    if error_handler is not None:
        dotted = DottedNameResolver(package)
        error_handler = dotted.maybe_resolve(error_handler)
    if default_filters is not None:
        if not is_nonstr_iter(default_filters):
            default_filters = list(filter(
                None, default_filters.splitlines()))
    if imports is not None:
        if not is_nonstr_iter(imports):
            imports = list(filter(None, imports.splitlines()))
    if preprocessor is not None:
        dotted = DottedNameResolver(package)
        preprocessor = dotted.maybe_resolve(preprocessor)


    return config.registry.queryUtility(IMakoLookupFactory)(
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

def includeme(config, _settings_prefix=_settings_prefix):
    settings = config.registry.settings
    download_if_notfound_helper = MakoRendererFactoryHelper(_settings_prefix)

    FailbackClass = config.maybe_dotted(settings[_settings_prefix+"failback.lookup"])
    lookup_factory = HasFailbackTemplateLookupFactory(
        FailbackClass.from_settings(settings, prefix=_settings_prefix), 
        settings[_settings_prefix+"renderer.name"])

    # don't have to lock?'
    registry_lock.acquire()
    config.registry.registerUtility(lookup_factory, IMakoLookupFactory)
    lookup = _make_lookup(config, _settings_prefix=_settings_prefix)
    config.registry.registerUtility(lookup, IMakoLookup, name=_settings_prefix)
    registry_lock.release()
    config.add_renderer(lookup_factory.name, download_if_notfound_helper)
