# encoding: utf-8
## todo:
from zope.interface import Interface
from zope.interface import provider
from zope.interface import implementer
from pyramid.renderers import RendererHelper
import ticketing.core.api as core_api
from ticketing.users.models import Membership
from sqlalchemy.orm.exc import NoResultFound
import logging

logger = logging.getLogger(__name__)

_lookup_key = "**selectable"
def includeme(config):
    config.add_renderer(_lookup_key, SelectableRenderer)
    config.add_directive("add_selectable_renderer_selector", add_selectable_renderer_selector)

def add_selectable_renderer_selector(config, fun):
    fun = config.maybe_dotted(fun)
    config.registry.registerUtility(provider(ISelectableRendererSelector)(fun))

class NoRenderableTemplateSetError(Exception):
    pass

class ISelectableRendererSelector(Interface):
    def __call__(vals, system_vals, request=None):
        """
        リクエストから、レンダリング対象となるテンプレートを決定する。
        テンプレートが決定できない場合は
        デフォルトのパスをビルドして返す。
        """
        pass

class StringLike(str):
    pass

class SkinnyRendererHelper(RendererHelper):
    #@override
    def render(self, value, system_values, request=None):
        renderer = self.renderer
        return renderer(value, system_values)

class SelectableRenderer(object):
    def __init__(self, info):
        self.info = info
        ## xxx: this is hack.
        self.path_format = self.info.name._path_format
        self.renderers = {}

    def get_sub_renderer(self, path):
        renderer = self.renderers.get(path)
        if renderer:
            return renderer
        renderer = SkinnyRendererHelper(name=path,
                                        package=self.info.package,
                                        registry=self.info.registry)
        self.renderers[path] = renderer
        return renderer

    @property
    def default_renderer(self):
        return self.get_sub_renderer('__default__')

    def __call__(self, value, system_values, request=None):
        request = request or system_values["request"]
        selector = request.registry.getUtility(ISelectableRendererSelector)
        try:
            renderer = self.get_sub_renderer(selector(self, value, system_values, request=request))
        except NoRenderableTemplateSetError as e:
            return self.default_renderer.render('notfound.html', system_values, request)
        return renderer.render(value, system_values, request=request)

def selectable_renderer(fmt, defaults=None):
    global _lookup_key
    lookup_key = StringLike(_lookup_key)
    lookup_key._path_format = fmt
    return lookup_key

## individual utility


def build_renderer_path(path_format, membership):
    return path_format % dict(membership=membership)

@implementer(ISelectableRendererSelector)
class ByDomainMappingSelector(object):
    def __init__(self, mapping):
        self.mapping = mapping

    def __call__(self, helper, value, system_values, request=None):
        assert request
        organization = core_api.get_organization(request)
        try:
            return build_renderer_path(helper.path_format, membership=organization.short_name)
        except NoResultFound:
            logger.warning("No matching template configuration found: using default configuration")
            return build_renderer_path(helper.path_format, membership='__default__')

