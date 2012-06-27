# -*- coding:utf-8 -*-

from ..interfaces import IOrderDelivery, IOrderPayment
from ..interfaces import ICartDelivery, ICartPayment
from ..interfaces import IPaymentPlugin, IDeliveryPlugin
from ..interfaces import IPaymentDeliveryPlugin
from . import logger

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
