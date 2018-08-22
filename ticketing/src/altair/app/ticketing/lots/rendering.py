# encoding: utf-8
import cgi
import logging
import os

from altair.app.ticketing.core.utils import search_template_file
from altair.pyramid_dynamic_renderer import RendererHelperProxy
from altair.pyramid_dynamic_renderer.interfaces import IDynamicRendererHelperFactory
from pyramid.interfaces import IRendererInfo
from pyramid.path import AssetResolver
from pyramid.renderers import RendererHelper
from zope.interface import implementer
from zope.proxy import ProxyBase, setProxiedObject

logger = logging.getLogger(__name__)


@implementer(IRendererInfo)
class NotFoundRenderer(object):
    name = None
    package = None
    type = None
    registry = None

    def __init__(self):
        pass

    def render(self, value, system_values, request):
        url = request.organization.emergency_exit_url
        if url:
            request.response.status = 302
            request.response.content_type = u'text/html'
            request.response.headers['Location'] = url
            return u'<html><body>{url}</body></html>'.format(url=cgi.escape(url))
        else:
            request.response.status = 404
            request.response.content_type = u'text/html'
            return u'<html><body><h1>404 Not Found</h1></body></html>'


@implementer(IDynamicRendererHelperFactory)
class OverridableTemplateRendererHelperFactory(object):
    def __init__(self, package, view_context_factory, path_patterns):
        self.bad_templates = set()
        self.package = package
        self.view_context_factory = view_context_factory
        self.path_patterns = path_patterns

    def get_template_path(self, view_context, their_package, path):
        for path_pattern in self.path_patterns:
            params = dict(
                their_package=their_package,
                subtype=(view_context.subtype or "__default__"),
            )

            file_path = search_template_file(view_context, path, self.package, path_pattern, params, log_err=False)
            if file_path:
                return file_path

        # パスパターンの中に該当するものが見つからなかった場合
        return None

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
        resolved_uri = self.get_template_path(view_context, package.__name__, name)
        if not resolved_uri:
            return NotFoundRenderer()

        return RendererHelper(name=resolved_uri, package=package, registry=registry)


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
                u'{package}:templates/{organization_short_name}/{ua_type}/{path}',
            ]
        )
    )
