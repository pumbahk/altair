# -*- coding:utf-8 -*-
import logging
from .interfaces import IOrderDelivery, IOrderPayment
from .interfaces import IGetCart
from .interfaces import IPaymentDeliveryPlugin
from .interfaces import IPaymentPlugin, IDeliveryPlugin
from .interfaces import IPaymentViewRendererLookup

logger = logging.getLogger(__name__)

def add_payment_delivery_plugin(config, plugin, payment_plugin_id, delivery_plugin_id):
    config.registry.utilities.register([], IPaymentDeliveryPlugin, 
        "payment-%s:delivery-%s" % (payment_plugin_id, delivery_plugin_id), plugin)

def add_payment_plugin(config, plugin, plugin_id):
    """ プラグイン登録 
    :param plugin: an instance of IPaymentPlugin 
    """
    
    logger.debug("add_payment_plugin: %s" % plugin_id)
    config.registry.utilities.register([], IPaymentPlugin, "payment-%s" % plugin_id, plugin)

def add_delivery_plugin(config, plugin, plugin_id):
    """ プラグイン登録 
    :param plugin: an instance of IDeliveryPlugin 
    """
    config.registry.utilities.register([], IDeliveryPlugin, "delivery-%s" % plugin_id, plugin)


def set_cart_getter(config, getter):
    getter = config.maybe_dotted(getter)
    reg = config.registry
    reg.registerUtility(getter, IGetCart)

def add_payment_view_renderer_lookup(config, impl, type):
    config.registry.utilities.register([], IPaymentViewRendererLookup, type, impl)
