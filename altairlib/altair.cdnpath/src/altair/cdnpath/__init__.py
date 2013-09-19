from zope.interface import implementer
from pyramid.interfaces import (
    IStaticURLInfo, 
    PHASE2_CONFIG
    )
from .interfaces import IStaticURLInfoFactory
from pyramid.config.views import StaticURLInfo
from pyramid.exceptions import ConfigurationError
from pyramid.compat import (
    WIN,
    url_quote
    )
from urlparse import urljoin, urlparse

def validate_url(url):
    parsed = urlparse(url)
    if (not any(p == parsed.scheme for p in ["http", "https"]) or
        parsed.netloc):
        raise ConfigurationError("{0} is not valid url")


@implementer(IStaticURLInfo)
class PrefixedStaticURLInfo(StaticURLInfo):
    def __init__(self, prefix, exclude=None, mapping=None):
        self.prefix = prefix
        self.exclude = exclude
        if self.exclude:
            self.generate = self._generate_with_exclude
        else:
            self.generate = self._generate
        self.spec_to_path_prefix_mapping = mapping or {}

    def validate(self):
        class request:
            environ = {}
        url = self._after_generate(request, "/foo/bar/txt")
        validate_url(url)
        
    def _after_generate(self, path, request, kwargs):
        return "//{0}{1}".format(self.prefix, path)

    def _generate_with_exclude(self, path, request, **kwargs):
        if self.exclude(path):
            return StaticURLInfo.generate(self, path, request, **kwargs)
        else:
            return self._generate(path, request, **kwargs)
    
    def _generate(self, path, request, **kwargs):
        registry = request.registry
        for (url, spec, route_name) in self._get_registrations(registry):
            if path.startswith(spec):
                subpath = path[len(spec):]
                if WIN: # pragma: no cover
                    subpath = subpath.replace('\\', '/') # windows

                custom_prefix = self.spec_to_path_prefix_mapping.get(spec)
                if custom_prefix:
                    return self._after_generate(custom_prefix+subpath, request, kwargs)
                elif url is None:
                    kwargs['subpath'] = subpath
                    return self._after_generate(request.route_path(route_name, **kwargs), request, kwargs)
                else:
                    return self._after_generate(url_quote(subpath), request, kwargs)

        raise ValueError('No static URL definition matching %s' % path)

@implementer(IStaticURLInfoFactory)
class S3StaticPathFactory(object):
    def __init__(self, bucket_name, exclude=None, prefix=None, mapping=None):
        self.bucket_name = bucket_name
        self.exclude = exclude
        self.prefix = self._get_correct_prefix(prefix)
        self.mapping = mapping

    def _get_correct_prefix(self, prefix):
        if prefix is None:
            return ""
        elif not prefix.startswith("/"):
            return "/"+prefix
        else:
            return prefix
        
    def __call__(self):
        prefix = "{0}.s3.amazonaws.com{1}".format(self.bucket_name, self.prefix)
        return PrefixedStaticURLInfo(prefix, self.exclude, mapping=self.mapping)

def add_cdn_static_path(config, factory=None):
    def register():
        info = factory()
        if hasattr(info, "validate"):
            info.validate
        config.registry.registerUtility(info, IStaticURLInfo)
    config.action(IStaticURLInfo, register, order=PHASE2_CONFIG)

def includeme(config):
    config.add_directive("add_cdn_static_path", add_cdn_static_path)
