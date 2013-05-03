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
from pyramid.interfaces import IRendererFactory
from pyramid.path import AssetResolver
import logging
logger = logging.getLogger()
from zope.interface import implementer
from zope.interface import Interface
from altair.pyramid_boto.s3.assets import DefaultS3RetrieverFactory
from altair.pyramid_boto.s3.assets import S3AssetResolver
from altair.pyramid_boto.s3.connection import DefaultS3ConnectionFactory

class IMakoLookupFactory(Interface):
    def __call__(*args, **kwargs):
        pass

class IFailbackLookup(Interface):
    def __call__(lookup, uri):
        """return template"""

#utility
def get_renderer_factory(request, filename):
    ext = os.path.splitext(filename)[1]
    return request.registry.queryUtility(IRendererFactory, name=ext)

def create_file_from_io(name, io):
    try:
        with open(name, "wb") as wf:
            shutil.copyfileobj(io, wf)
    except IOError:
        os.makedirs(os.path.dirname(name).rstrip(".."))
        with open(name, "wb") as wf:
            shutil.copyfileobj(io, wf)

def create_adjusted_name(uri):
    return uri.replace(':', '$')


class TemplateLookupEvents(object):
    __slots__ = ("events", )
    def __init__(self, **events):
        self.events = events or {}

    def exists(self, key):
        return key in self.events

    def fire(self, key, *args, **kwargs):
        event = self.events.pop(key)
        event(*args, **kwargs)

    def fire_if_exists(self, key, *args, **kwargs):
        return self.exists(key) and self.fire(key, *args, **kwargs)


@implementer(IMakoLookup)
class HasFailbackTemplateLookup(PkgResourceTemplateLookup):
    Events = TemplateLookupEvents
    def __init__(self, failback_lookup, *args, **kwargs):
        self.failback_lookup = failback_lookup
        self._events = self.Events()
        super(HasFailbackTemplateLookup, self).__init__(*args, **kwargs)

    def add_event(self, k, fn):
        self._events.events[k] = fn

    def get_template_failback(self, uri): #need cache
        return self.failback_lookup(self, uri)

    def get_template(self, uri):
        try:
            self._events.fire_if_exists(uri, self)
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


class AssetSpecManager(object):
    def __init__(self, assetspec):
        self.assetspec = assetspec
        self.default_directory = AssetResolver().resolve(assetspec).abspath()        
        if not ":" in assetspec:
            self.prefix = assetspec+":"
        else:
            self.prefix = assetspec.rstrip("/")+"/"    

    def is_assetspec(self, uri):
        return ":" in uri

    def as_assetspec(self, uri):
        if not self.is_assetspec(uri):
            return "{0}{1}".format(self.prefix, uri)
        return uri


@implementer(IFailbackLookup)
class DefaultFailbackLookup(object):
    def __init__(self, host, assetspec):
        self.host = host.rstrip("/")
        self.asset_spec_manager = AssetSpecManager(assetspec)

    @classmethod 
    def from_settings(cls, settings, prefix=""):
        return cls(settings[prefix+"lookup.host"], 
                   settings[prefix+"directories"][0])

    def __call__(self, lookup, uri):
        uri = self.asset_spec_manager.as_assetspec(uri)
        lookup_url = "{0}/{1}".format(self.host, uri.lstrip("/"))
        res = urllib.urlopen(lookup_url)
        if res.getcode() != 200:
            return None
        adjusted = create_adjusted_name(uri)
        srcfile = AssetResolver().resolve(uri).abspath()
        create_file_from_io(srcfile, res)
        return lookup._load(srcfile, adjusted)


@implementer(IFailbackLookup)
class S3FailbackLookup(object):
    def __init__(self, assetspec, access_key, secret_key, bucket, delimiter):
        self.asset_spec_manager = AssetSpecManager(assetspec)
        self.connection = DefaultS3ConnectionFactory(access_key, secret_key)()
        self.retriver_factory = DefaultS3RetrieverFactory()

    @classmethod 
    def from_settings(cls, settings, prefix=""):
        return cls(settings[prefix+"directories"][0], 
                   settings[prefix+"access_key"], 
                   settings[prefix+"secret_key"], 
                   settings[prefix+"bucket"], 
                   settings.get(prefix+"delimiter", "/"))

    def __call__(self, lookup, uri):
        uri = self.asset_spec_manager.as_assetspec(uri)
        resolver = S3AssetResolver(self.connection, self.retriver_factory, delimiter=self.delimiter)
        descriptor = resolver.resolve(uri)
        if not descriptor.exists():
            return None
        adjusted = create_adjusted_name(uri)
        srcfile = AssetResolver().resolve(uri).abspath()
        create_file_from_io(srcfile, descriptor.stream())
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
    directories = [ AssetResolver().resolve(d).abspath() for d in directories ]
    if module_directory is not None:
        module_directory = AssetResolver().resolve(module_directory).abspath()
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
