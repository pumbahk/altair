# -*- coding:utf-8 -*-

from ticketing.payments.interfaces import IOrderDelivery, IOrderPayment
from ticketing.cart.interfaces import ICartDelivery, ICartPayment
from ticketing.payments.interfaces import IPaymentDeliveryPlugin
from ticketing.payments.interfaces import IPaymentPlugin, IDeliveryPlugin
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
