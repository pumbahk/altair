# -*- coding:utf-8 -*-
def includeme(config):
    config.add_route("dummy.orderreview.index", "/dummy")
    config.add_route("dummy.orderreview.qr", "/dummy/qr")
    config.scan(".views")
