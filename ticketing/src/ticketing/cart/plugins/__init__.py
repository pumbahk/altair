# -*- coding:utf-8 -*-
import hashlib
import logging

from pyramid.view import view_config
from pyramid.response import Response
from .interfaces import IPaymentPlugin, IDeliveryPlugin

logger = logging.getLogger(__name__)

def includeme(config):
    config.scan(".")
    config.add_directive("add_payment_plugin", ".directives.add_payment_plugin")
    config.add_directive("add_delivery_plugin", ".directives.add_delivery_plugin")

    config.include(".multicheckout")
    config.include(".reservednumber")
    config.include(".shipping")
    #config.include(".anshin")
    #config.icnlude(".sej")
    #config.icnlude(".sej")


def get_payment_plugin(request, plugin_id):
    logger.debug("get_payment_plugin: %s" % plugin_id)
    registry = request.registry
    return registry.utilities.lookup([], IPaymentPlugin, name="payment-%s" % plugin_id)

def get_delivery_plugin(request, plugin_id):
    registry = request.registry
    return registry.utilities.lookup([], IDeliveryPlugin, name="delivery-%s" % plugin_id)
