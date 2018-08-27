# encoding: utf-8
import logging

from altair.app.ticketing.core.utils import search_template_file
from altair.pyramid_dynamic_renderer import RendererHelperProxy, RequestSwitchingRendererHelperFactory
from altair.pyramid_dynamic_renderer.interfaces import IDynamicRendererHelperFactory
from pyramid.renderers import RendererHelper
from zope.interface import implementer

logger = logging.getLogger(__name__)

@implementer(IDynamicRendererHelperFactory)
class OverridableTemplateRendererHelperFactory(object):
    def __init__(self, package, view_context_factory, path_patterns):
        self.bad_templates = set()
        self.package = package
        self.view_context_factory = view_context_factory
        self.path_patterns = path_patterns

    def get_template_path(self, view_context, their_package, path):
        for path_pattern in self.path_patterns:
            login_body = u'__fc_auth__' if view_context.membership_login_body else u''
            params = dict(
                their_package=their_package,
                membership=(unicode(view_context.membership) or u"__default__"),
                login_body=login_body,
            )

            if path_pattern == u'{package}:templates/{login_body}/{ua_type}/{path}' and not login_body:
                continue

            file_path = search_template_file(view_context, path, self.package, path_pattern, params, log_err=False)
            if file_path:
                return file_path

        # パスパターンの中に該当するものが見つからなかった場合
        return None

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
        return RendererHelper(name=resolved_uri, package=package, registry=registry)


selectable_renderer_helper_factory = RequestSwitchingRendererHelperFactory(
    fallback_renderer='notfound.html',
    name_builder=lambda name, view_context, request: view_context.get_template_path(name),
    view_context_factory=lambda name, package, registry, request, **kwargs: request.view_context
    )


def selectable_renderer(name):
    return RendererHelperProxy(
        selectable_renderer_helper_factory,
        name
        )
