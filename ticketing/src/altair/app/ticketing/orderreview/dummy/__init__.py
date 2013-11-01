# -*- coding:utf-8 -*-
def includeme(config):
    config.add_route("dummy.orderreview.index", "/dummy")
    config.add_route("dummy.orderreview.qr", "/dummy/qr")
    config.add_route("dummy.orderreview.qrdraw", "/dummy/qr/{ticket_id}/{sign}/image")
    config.scan(".views")
