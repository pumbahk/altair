# encoding: utf-8
import os
import logging
from zope.interface import implementer
from zope.proxy import ProxyBase, setProxiedObject
from pyramid.renderers import RendererHelper
from pyramid.path import AssetResolver
from altair.pyramid_dynamic_renderer.interfaces import IDynamicRendererHelperFactory
from altair.pyramid_dynamic_renderer import RendererHelperProxy, RequestSwitchingRendererHelperFactory

logger = logging.getLogger(__name__)

@implementer(IDynamicRendererHelperFactory)
class OverridableTemplateRendererHelperFactory(object):
    def __init__(self, package, view_context_factory, path_patterns):
        self.bad_templates = set()
        self.package = package
        self.view_context_factory = view_context_factory
        self.path_patterns = path_patterns

    def get_template_paths(self, view_context, their_package, path):
        params = dict(
            package=self.package,
            their_package=their_package,
            organization_short_name=(view_context.organization_short_name or "__default__"),
            subtype=(view_context.subtype or "__default__"),
            ua_type=view_context.ua_type,
            path=path
            )
        return [
            path_pattern % params
            for path_pattern in self.path_patterns
            ]

    def resolve_template(self, spec):
        package_or_path, colon_in_name, path = spec.partition(':')
        if colon_in_name:
            if os.path.isabs(path):
                # absolute path, possibly with colon (e.g. C:\\Users\\foo...)
                package = None
                path = urllib.pathname2url(spec)
            else:
                # absolute path specification (e.g. some.pkg:foo/bar/baz.html)
                package = package_or_path
        else:
            # relative path specification (e.g. foo/bar/baz.html)
            package = self.package
            path = package_or_path
        return AssetResolver(package).resolve(path)

    def __call__(self, name, package, registry, request=None, system_values=None, **kwargs):
        if request is None:
            logger.warning('request is None')
            return None
        view_context = None
        if self.view_context_factory is not None:
            view_context = self.view_context_factory(name, package, registry, request, system_values=system_values, **kwargs)
        if system_values is not None:
            system_values['view_context'] = view_context
        paths = self.get_template_paths(view_context, package.__name__, name)
        for path in paths:
            asset = self.resolve_template(path)
            resolved_uri = asset.absspec()
            if resolved_uri in self.bad_templates:
                continue
            else:
                if not asset.exists():
                    logger.debug('template %s does not exist' % resolved_uri)
                    self.bad_templates.add(resolved_uri)
                    continue
            return RendererHelper(name=resolved_uri, package=package, registry=registry)
        return None

_template_renderer_helper_factory_proxy = ProxyBase(None)

def selectable_renderer(name):
    return RendererHelperProxy(
        _template_renderer_helper_factory_proxy,
        name
        )

def includeme(config):
    setProxiedObject(
        _template_renderer_helper_factory_proxy,
        OverridableTemplateRendererHelperFactory(
            config.registry.__name__,
            view_context_factory=lambda name, package, registry, request, **kwargs: request.view_context,
            path_patterns=[
                'templates/%(organization_short_name)s/%(subtype)s/%(ua_type)s/%(path)s',
                'templates/%(organization_short_name)s/__default__/%(ua_type)s/%(path)s',
                'templates/__default__/%(subtype)s/%(ua_type)s/%(path)s',
                'templates/__default__/__default__/%(ua_type)s/%(path)s',
                ]
            )
        )

