# -*- coding: utf-8 -*-

from altair.app.ticketing import newRootFactory
from .resources import PerformanceAdminResource

def includeme(config):
    factory = newRootFactory(PerformanceAdminResource)
    config.add_route('products.index', '/products/{performance_id}', factory=factory)
    config.add_route('performances.index', '/{event_id}', factory=factory)
    config.add_route('performances.new', '/new/{event_id}', factory=factory)
    config.add_route('performances.show', '/show/{performance_id}', factory=factory)
    config.add_route('performances.show_tab', '/show/{performance_id}/{tab}', factory=factory)
    config.add_route('performances.edit', '/edit/{performance_id}', factory=factory)
    config.add_route('performances.delete', '/delete/{performance_id}', factory=factory)
    config.add_route('performances.copy', '/copy/{performance_id}', factory=factory)
    config.add_route('performances.open', '/open/{performance_id}', factory=factory)
    config.add_route("performances.mailinfo.index", "/mailinfo/{performance_id}", factory=factory)
    config.add_route("performances.mailinfo.edit", "/mailinfo/{performance_id}/mailtype/{mailtype}", factory=factory)

    config.add_route('performances.import_orders.index', '/import_orders/{performance_id}', factory=factory)
    config.add_route('performances.import_orders.confirm', '/import_orders/{performance_id}/confirm', factory=factory)
    config.add_route('performances.import_orders.completed', '/import_orders/{performance_id}/completed', factory=factory)
    config.add_route('performances.import_orders.clear', '/import_orders/{performance_id}/clear', factory=factory)
