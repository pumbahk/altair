# -*- coding:utf-8 -*-
import hashlib
import logging

from pyramid.view import view_config
from pyramid.response import Response

logger = logging.getLogger(__name__)

MULTICHECKOUT_PAYMENT_PLUGIN_ID = 1
CHECKOUT_PAYMENT_PLUGIN_ID = 2
SEJ_PAYMENT_PLUGIN_ID = 3
RESERVE_NUMBER_PAYMENT_PLUGIN_ID = 4

SHIPPING_DELIVERY_PLUGIN_ID = 1
SEJ_DELIVERY_PLUGIN_ID = 2
RESERVE_NUMBER_DELIVERY_PLUGIN_ID = 3
QR_DELIVERY_PLUGIN_ID = 4

_template = None

def setup_template(config):
    from pyramid_selectable_renderer import SelectableRendererSetup
    from pyramid_selectable_renderer.interfaces import IReceiveArguments
    from pyramid_selectable_renderer.custom import SelectByRequestGen
    from pyramid.renderers import get_renderer
    from pyramid.interfaces import IRendererFactory
    from ..interfaces import IPaymentViewRendererLookup
    from zope.interface import implementer, provider

    @provider(IRendererFactory)
    def overridable(path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
        return get_renderer('%s:templates/%s' % (__name__, path_or_renderer_name), package=__name__)

    default_renderer_factories = {
        'overridable': overridable,
        }

    @implementer(IReceiveArguments)
    class Env(object):
        def __init__(self, path_or_renderer_name, type, for_, plugin_type, plugin_id, **kwargs):
            self.package = __name__
            self.path_or_renderer_name = path_or_renderer_name
            self.type = type
            self.for_ = for_
            self.plugin_type = plugin_type
            self.plugin_id = plugin_id
            self.kwargs = kwargs

        def __repr__(self):
            return 'Env(path_or_renderer_name=%r, type=%r, for_=%r, plugin_type=%r, plugin_id=%r, **kwargs=%r)' % (
                self.path_or_renderer_name,
                self.type,
                self.for_,
                self.plugin_type,
                self.plugin_id,
                self.kwargs
                )

    class Renderer(object):
        def __init__(self, info):
            self.info = info

        def __call__(self, env, value, system_values, request):
            logger.debug('info.name=%r, info.package=%r, env=%r' % (self.info.name, self.info.package, env))
            lookup = request.registry.queryUtility(IPaymentViewRendererLookup, env.type)
            renderer = None
            if lookup is not None:
                renderer = lookup(env.path_or_renderer_name, self.info, env.for_, env.plugin_type, env.plugin_id, **env.kwargs)
                logger.debug('renderer lookup => %r' % renderer)
            if renderer is None:
                renderer_factory = default_renderer_factories.get(env.type)
                if renderer_factory is not None:
                    renderer = renderer_factory(env.path_or_renderer_name, self.info, env.for_, env.plugin_type, env.plugin_id, **env.kwargs)
                    logger.debug('renderer from default_renderer_factories => %r' % renderer)
            if renderer is None:
                renderer = get_renderer(env.path_or_renderer_name, self.info.package)
                logger.debug('fallback renderer => %r' % renderer)
            return renderer(value, system_values)

    retval = SelectableRendererSetup(Env, Renderer,
        renderer_name='%s:selectable_renderer' % __name__.replace('.', ':')
        )
    retval.register_to(config)
    return retval


def includeme(config):
    global _template
    _template = setup_template(config)
    config.add_static_view('static', 'altair.app.ticketing.payments.plugins:static', cache_max_age=3600)
    config.include(".multicheckout")
    config.include(".reservednumber")
    config.include(".shipping")
    config.include(".sej")
    config.include(".checkout")
    config.include(".qr")
