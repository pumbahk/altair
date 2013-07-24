# -*- coding:utf-8 -*-

""" TBA
"""

from . import helpers as h

def add_payment_method(config, payment_method_id, route_name):
    payment_method_manager = h.get_payment_method_manager(registry=config.registry)
    payment_method_manager.add_route_name(payment_method_id, route_name)
