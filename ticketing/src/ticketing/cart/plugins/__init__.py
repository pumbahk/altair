# -*- coding:utf-8 -*-
import hashlib
import logging

from pyramid.view import view_config
from pyramid.response import Response

logger = logging.getLogger(__name__)

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


