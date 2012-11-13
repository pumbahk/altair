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


def includeme(config):
    config.add_directive("add_payment_plugin", ".directives.add_payment_plugin")
    config.add_directive("add_delivery_plugin", ".directives.add_delivery_plugin")
    config.add_directive("add_payment_delivery_plugin", ".directives.add_payment_delivery_plugin")
    config.add_static_view('static', 'ticketing.cart.plugins:static', cache_max_age=3600)

    config.include(".multicheckout")
    config.include(".reservednumber")
    config.include(".shipping")
    config.include(".sej")
    config.include(".checkout")
    config.include(".qr")


