# -*- coding:utf-8 -*-
def includeme(config):
    config.add_route("refresh.token", "/refresh/token/{token_id}")
    config.add_endpoint_route("refresh.order", "/refresh/order")
    config.add_endpoint_route("refresh.order.qr", "/refresh/order/qr")
    config.add_endpoint_route("refresh.order2", "/refresh/order2")
    config.scan(".views")
