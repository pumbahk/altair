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
    config.add_route('performances.reservation', '/reservation/{performance_id}', factory=factory)
    config.add_route('performances.reservation.stock.edit', '/reservation/{performance_id}/stock/edit/{stock_id}', factory=factory)
    config.add_route('performances.edit', '/edit/{performance_id}', factory=factory)
    config.add_route('performances.delete', '/delete/{performance_id}', factory=factory)
    config.add_route('performances.copy', '/copy/{performance_id}', factory=factory)
    config.add_route('performances.manycopy', '/manycopy/{performance_id}', factory=factory)
    config.add_route('performances.termcopy', '/termcopy/{performance_id}', factory=factory)
    config.add_route('performances.open', '/open/{performance_id}', factory=factory)
    config.add_route("performances.mailinfo.index", "/mailinfo/{performance_id}", factory=factory)
    config.add_route("performances.mailinfo.edit", "/mailinfo/{performance_id}/mailtype/{mailtype}", factory=factory)
    # find performance by performance code
    config.add_route('performances.search.find_by_code', '/search/find_by_code')

    config.add_route('performances.import_orders.index', '/import_orders/{performance_id}', factory=factory)
    config.add_route('performances.import_orders.confirm', '/import_orders/{performance_id}/confirm', factory=factory)
    config.add_route('performances.import_orders.show', '/import_orders/{performance_id}/show/{task_id}', factory=factory)
    config.add_route('performances.import_orders.delete', '/import_orders/{performance_id}/delete/{task_id}', factory=factory)
    config.add_route('performances.import_orders.test_version', '/import_orders/{performance_id}/test_version', factory=factory)
    config.add_route('performances.import_orders.error_list.download', '/import_orders/{task_id}/error_list/download', factory=factory)

    config.add_route('performances.region.index', '/drawing/{performance_id}', factory=factory)
    config.add_route('performances.region.update', '/drawing/{performance_id}/update', factory=factory)

    config.add_route('performances.orion.index', '/orion/{performance_id}', factory=factory)

    config.add_route('performances.resale.index', '/resale/{performance_id}', factory=factory)
    # send to orion api
    config.add_route('performances.resale.send_resale_segment_to_orion', '/resale/eg_send/resale_segment', factory=factory)
    config.add_route('performances.resale.send_resale_request_to_orion', '/resale/eg_send/resale_request', factory=factory)
    config.add_route('performances.resale.send_all_resale_request_to_orion', '/resale/eg_send/all_resale_request', factory=factory)
    config.add_route('performances.resale.requests.operate', '/resale/requests/operate', factory=factory)

    ##altair.app.ticketing.print_progress.__init__.pyでperformances.print_progress.showが定義されている

    config.add_route('performances.discount_code_settings.show', '/discount_code_settings/{performance_id}', factory=factory)

    config.add_route('performances.price_batch_update.index', '/price_batch_update/{performance_id}', factory=factory)
    config.add_route('performances.price_batch_update.confirm',
                     '/price_batch_update/{performance_id}/confirm', factory=factory)
    config.add_route('performances.price_batch_update.show',
                     '/price_batch_update/{performance_id}/show/{task_id}', factory=factory)
    config.add_route('performances.price_batch_update.delete',
                     '/price_batch_update/{performance_id}/delete', factory=factory)
    config.add_route('performances.price_batch_update.cancel',
                     '/price_batch_update/{performance_id}/cancel', factory=factory)

VISIBLE_PERFORMANCE_SESSION_KEY = '_visible_performance'
