import re
import os
from zope.interface.declarations import implementer, provider
from pyramid.renderers import RendererHelper
from pyramid.path import DottedNameResolver
from ..interfaces import ITrackingCodeInjector, ITrackingCodeInjectorFactory

_head_regex = re.compile('(</head>)', re.IGNORECASE)

def fixup_template_path(template):
    rest, ext = os.path.splitext(template)
    if not ext:
        template = rest + '.mako'
    if ':' not in template:
        template = __name__ + ':' + template
    return template

def get_renderer(name, package, factory=None):
    info = RendererHelper(name=name, package=package)
    if factory is not None:
        return factory(info)
    else:
        return info.renderer

@implementer(ITrackingCodeInjector)
@provider(ITrackingCodeInjectorFactory)
class GoogleAnalyticsInjector(object):
    def __init__(self, type_, tracking_id, domain='', base_domain='', renderer_factory='pyramid.mako_templating.renderer_factory', template=None):
        self.tracking_id = tracking_id
        self.domain = domain
        self.base_domain = base_domain
        if template is None:
            template = 'standard'
        template = fixup_template_path(template)
        resolver = DottedNameResolver(__name__)
        if renderer_factory:
            renderer_factory_ = resolver.maybe_resolve(renderer_factory)
        else:
            renderer_factory_ = None
        self.renderer = get_renderer(template, __name__, renderer_factory_)

    def __call__(self, request, response):
        result = self.renderer(self.__dict__, { 'request': request })
        response.text = _head_regex.sub('\n%s\n\\1' % result, response.text, count=1)
        return response

def includeme(config):
    config.registry.registerUtility(GoogleAnalyticsInjector, ITrackingCodeInjectorFactory, 'google_analytics')
