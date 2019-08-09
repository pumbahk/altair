# -*- coding:utf-8 -*-
from .resources import MiniAdminResourceBase, MiniAdminLotResource


def includeme(config):
    config.add_route('mini_admin.index', '/', factory='.resources.MiniAdminResourceBase')
    config.add_route('mini_admin.report', '/report/{event_id}', factory='.resources.MiniAdminReportResource')
    config.add_route('mini_admin.order_search', '/order_search/{event_id}',
                     factory='.resources.MiniAdminOrderSearchResource')
    config.add_route('mini_admin.lot.report', '/lot/report/{lot_id}', factory='.resources.MiniAdminLotResource')
    config.scan(".")
