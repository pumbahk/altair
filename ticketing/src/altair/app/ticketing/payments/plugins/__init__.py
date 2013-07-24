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
    config.add_static_view('static', 'altair.app.ticketing.payments.plugins:static', cache_max_age=3600)
    config.include(".multicheckout")
    config.include(".reservednumber")
    config.include(".shipping")
    config.include(".sej")
    config.include(".checkout")
    config.include(".qr")


