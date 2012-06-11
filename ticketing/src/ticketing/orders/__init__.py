# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('orders.index', '/')
    config.add_route('orders.show', '/show/{order_id}')

    config.add_route('orders.sej'           , '/sej')
    config.add_route('orders.sej.order.request'   , '/sej/order/request')

    config.add_route('orders.sej.order.update'   , '/sej/order/{order_id}/update')
    config.add_route('orders.sej.order.cancel'   , '/sej/order/{order_id}/cancel')
    config.add_route('orders.sej.order.ticket.preview'   , '/sej/order/{order_id}/ticket/preview')


    config.scan(".")
