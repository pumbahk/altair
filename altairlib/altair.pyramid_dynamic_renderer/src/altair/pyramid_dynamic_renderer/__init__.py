# encoding: utf-8
from zope.interface import implementer
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.interfaces import IRendererInfo
from pyramid.threadlocal import get_current_request, get_current_registry
from pyramid.renderers import RendererHelper
from pyramid.compat import text_type

from .interfaces import ILateBoundRendererHelper, IDynamicRendererHelperFactory

import logging

logger = logging.getLogger(__name__)


@implementer(IRendererInfo, ILateBoundRendererHelper)
class RendererHelperProxy(RendererHelper):
    def __init__(self, helper_factory, name):
        super(RendererHelperProxy, self).__init__(name)
        self.registry = None
        self.renderer_helper_factory = helper_factory

    def bind(self, registry, package):
        self.registry = registry
        self.package = package

    @property
    def renderer(self):
        request = get_current_request()
        return self._get_renderer_helper(request=request).renderer

    def _get_renderer_helper(self, **kwargs):
        return self.renderer_helper_factory(
            self.name,
            self.package,
            self.registry,
            **kwargs
            )

    def render(self, value, system_values, request=None):
        if system_values is None:
            system_values = {
                'view':None,
                'context':getattr(request, 'context', None),
                'request':request,
                'req':request,
                }
        renderer_helper = self._get_renderer_helper(
            request=request,
            value=value,
            system_values=system_values,
            )
        system_values['renderer_name'] = renderer_helper.name
        system_values['renderer_info'] = renderer_helper
        return renderer_helper.render(value, system_values, request)

    def clone(self, name, package, registry):
        if name is None:
            name = self.name
        if package is None:
            package = self.package
        if registry is None:
            registry = self.registry
        retval = self.__class__(self.helper_factory, name)
        retval.bind(registry, package)
        return retval


class FallingBackRendererHelper(RendererHelper):
    def __init__(self, name, package, registry, fallback):
        super(FallingBackRendererHelper, self).__init__(name=name, package=package, registry=registry)
        self.fallback = fallback

    def render(self, value, system_values, request=None):
        try:
            return super(FallingBackRendererHelper, self).render(value, system_values, request)
        except Exception as e:
            logger.exception('failed to render')
            return self.fallback.render(value, system_values, request)

    def clone(self, name=None, package=None, registry=None):
        if name is None:
            name = self.name
        if package is None:
            package = self.package
        if registry is None:
            registry = self.registry
        return self.__class__(name=name, package=package, registry=registry, fallback=self.fallback)


@implementer(IDynamicRendererHelperFactory)
class RequestSwitchingRendererHelperFactory(object):
    renderer_helper_factory = RendererHelper

    def __init__(self, fallback_renderer, name_builder, view_context_factory=None):
        self.fallback_renderer = fallback_renderer
        self.name_builder = name_builder
        self.view_context_factory = view_context_factory

    def _fallback(self, package, registry):
        return RendererHelper(
            name=self.fallback_renderer,
            package=package,
            registry=registry
            )

    def __call__(self, name, package, registry, request=None, system_values=None, **kwargs):
        # try to retrieve request from the system vars when not directly provided 
        if request is None:
            if system_values is not None:
                request = system_values.get('request')
        if request is None:
            return self._fallback(package, registry)
        view_context = None
        if self.view_context_factory is not None:
            view_context = self.view_context_factory(name, package, registry, request=request, system_values=system_values, **kwargs)
        if system_values is not None:
            system_values['view_context'] = view_context
        name = self.name_builder(name, view_context, request)
        return self.renderer_helper_factory(
            name=name,
            package=package,
            registry=registry
            )


from .config import includeme, lbr_view_config
