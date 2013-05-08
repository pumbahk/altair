from zope.interface import implementer
from pyramid.interfaces import (
    IStaticURLInfo, 
    IRequest, 
    PHASE2_CONFIG
    )
from .interfaces import (
    ICDNStaticPathFactory, 
    ICDNStaticPath
    )
from pyramid.exceptions import ConfigurationError

@implementer(ICDNStaticPath)
class PrefixedStaticPath(object):
    def __init__(self, prefix, request):
        self.prefix = prefix
        self.request = request

    def static_path(self, path, **kwargs):
        return self.request.static_path(path, **kwargs)

    def static_url(self, path, **kwargs):
        if path.startswith("/"):
            return "{0}{1}".format(self.prefix, path)            
        return "{0}{1}".format(self.prefix, self.request.static_path(path, **kwargs))

@implementer(ICDNStaticPathFactory)
class S3StaticPathFactory(object):
    default_scheme = "http"
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def __call__(self, request):
        scheme = request.environ.get("wsgi.url_scheme") or self.default_scheme
        prefix = "{0}://{1}.s3.amazonaws.com".format(scheme, self.bucket_name)
        return PrefixedStaticPath(prefix, request)

def add_cdn_static_path(config, factory):
    def register():
        config.registry.adapters.register(IRequest, ICDNStaticPathFactory, name="", value=factory)
        config.set_request_property("altair.cdnpath.api.get_cdn_static_path", "cdn", reify=True)
        if config.registry.queryUtility(IStaticURLInfo) is None:
            raise ConfigurationError('No static URL definition. (need: config.add_static_view ?)')
    config.action(ICDNStaticPathFactory, register, order=PHASE2_CONFIG)

def includeme(config):
    config.add_directive("add_cdn_static_path", add_cdn_static_path)
