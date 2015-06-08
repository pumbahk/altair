# -*- coding: utf-8 -*-

from altair.app.ticketing import newRootFactory
from .resources import PerformanceAdminResource

def includeme(config):
    factory = newRootFactory(PerformanceAdminResource)
    config.add_route('performances.index', '/{event_id}', factory=factory)
    config.add_route('performances.visible','/visible/{event_id}', factory=factory)
    config.add_route('performances.invisible','/invisible/{event_id}', factory=factory)

    config.add_route('performances.new', '/new/{event_id}', factory=factory)
    config.add_route('performances.show', '/show/{performance_id}', factory=factory)
    config.add_route('performances.show_tab', '/show/{performance_id}/{tab}', factory=factory)
    config.add_route('performances.edit', '/edit/{performance_id}', factory=factory)
    config.add_route('performances.delete', '/delete/{performance_id}', factory=factory)
    config.add_route('performances.copy', '/copy/{performance_id}', factory=factory)
    config.add_route('performances.manycopy', '/manycopy/{performance_id}', factory=factory)
    config.add_route('performances.open', '/open/{performance_id}', factory=factory)
    config.add_route("performances.mailinfo.index", "/mailinfo/{performance_id}", factory=factory)
    config.add_route("performances.mailinfo.edit", "/mailinfo/{performance_id}/mailtype/{mailtype}", factory=factory)

    config.add_route('performances.import_orders.index', '/import_orders/{performance_id}', factory=factory)
    config.add_route('performances.import_orders.confirm', '/import_orders/{performance_id}/confirm', factory=factory)
    config.add_route('performances.import_orders.show', '/import_orders/{performance_id}/show/{task_id}', factory=factory)
    config.add_route('performances.import_orders.delete', '/import_orders/{performance_id}/delete/{task_id}', factory=factory)

    config.add_route('performances.orion.index', '/orion/{performance_id}', factory=factory)
    ##altair.app.ticketing.print_progress.__init__.pyでperformances.print_progress.showが定義されている

VISIBLE_PERFORMANCE_SESSION_KEY = '_visible_performance'
