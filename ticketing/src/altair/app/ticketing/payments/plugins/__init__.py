# -*- coding:utf-8 -*-
import hashlib
import logging

from zope.interface import implementer, provider

from pyramid.renderers import RendererHelper
from pyramid.compat import text_type

from altair.pyramid_dynamic_renderer import RendererHelperProxy
from altair.pyramid_dynamic_renderer.interfaces import IDynamicRendererHelperFactory

from ..interfaces import IPaymentViewRendererLookup

logger = logging.getLogger(__name__)

MULTICHECKOUT_PAYMENT_PLUGIN_ID = 1
CHECKOUT_PAYMENT_PLUGIN_ID = 2
SEJ_PAYMENT_PLUGIN_ID = 3
RESERVE_NUMBER_PAYMENT_PLUGIN_ID = 4
FREE_PAYMENT_PLUGIN_ID = 5

SHIPPING_DELIVERY_PLUGIN_ID = 1
SEJ_DELIVERY_PLUGIN_ID = 2
RESERVE_NUMBER_DELIVERY_PLUGIN_ID = 3
QR_DELIVERY_PLUGIN_ID = 4
ORION_DELIVERY_PLUGIN_ID = 5

class Env(text_type):
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

    def __new__(cls, *args, **kwargs):
        return text_type.__new__(cls)


@implementer(IDynamicRendererHelperFactory)
class PaymentPluginRendererHelperFactory(object):
    def __init__(self, default_renderer_factories):
        self.default_renderer_factories = default_renderer_factories

    def __call__(self, env, package, registry, request=None, system_values=None, **kwargs):
        # try to retrieve request from the system vars when not directly provided
        if request is None:
            if system_values is not None:
                request = system_values.get('request')

        logger.debug('env=%r' % env)
        lookup = request.registry.queryUtility(IPaymentViewRendererLookup, env.type)
        renderer = None
        if lookup is not None:
            renderer = lookup(request, env.path_or_renderer_name, env.for_, env.plugin_type, env.plugin_id, package, registry, system_values=system_values, **env.kwargs)
            logger.debug('renderer lookup => %r' % renderer)
        if renderer is None:
            renderer_factory = self.default_renderer_factories.get(env.type)
            if renderer_factory is not None:
                renderer = renderer_factory(request, env.path_or_renderer_name, env.for_, env.plugin_type, env.plugin_id, package, registry, system_values=system_values, **env.kwargs)
                logger.debug('renderer from default_renderer_factories => %r' % renderer)
        if renderer is None:
            renderer = RendererHelper(
                name=env.path_or_renderer_name,
                package=package,
                registry=registry
                )
            logger.debug('fallback renderer => %r' % renderer)
        return renderer


payment_plugin_renderer_helper_factory = PaymentPluginRendererHelperFactory(
    default_renderer_factories={
        'overridable': \
            lambda request, path_or_renderer_name, for_, \
                   plugin_type, plugin_id, package, registry, \
                   **kwargs: \
                RendererHelper(
                    '%s:templates/%s/%s' % (__name__, kwargs.get('fallback_ua_type', 'UNSPECIFIED'), path_or_renderer_name),
                    package=package,
                    registry=registry
                    )
        }
    )


def _template(*args, **kwargs):
    return RendererHelperProxy(
        payment_plugin_renderer_helper_factory,
        Env(*args, **kwargs)
        )

def includeme(config):
    config.include(".multicheckout")
    config.include(".reservednumber")
    config.include(".shipping")
    config.include(".sej")
    config.include(".checkout")
    config.include(".qr")
    config.include(".orion")
    config.include(".free")
