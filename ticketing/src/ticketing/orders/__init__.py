# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('orders.index', '/')
    config.add_route('orders.show', '/show/{order_id}')