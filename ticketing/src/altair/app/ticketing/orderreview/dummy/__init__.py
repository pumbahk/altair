# -*- coding:utf-8 -*-
def includeme(config):
    config.include('altair.pyramid_dynamic_renderer')
    config.add_route("dummy.orderreview.index", "/dummy")
    config.add_route("dummy.orderreview.show", "/dummy/show")
    config.add_route("dummy.orderreview.show.guest", "/dummy/guest")
    config.add_route("dummy.orderreview.qr", "/dummy/qr")
    config.add_route("dummy.orderreview.qrdraw", "/dummy/qr/{ticket_id}/{sign}/image")
    config.scan(".views")
