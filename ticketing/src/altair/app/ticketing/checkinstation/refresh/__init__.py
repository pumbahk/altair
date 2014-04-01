# -*- coding:utf-8 -*-
def includeme(config):
    config.add_route("refresh.token", "/refresh/token/{token_id}")
    config.add_route("refresh.order", "/refresh/order_no/{order_no}")
    config.scan(".views")
