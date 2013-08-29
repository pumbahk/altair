# -*- coding: utf-8 -*-

from altair.app.ticketing import newRootFactory
from .resources import SalesSegmentAdminResource

def includeme(config):
    factory = newRootFactory(SalesSegmentAdminResource)
    config.add_route('sales_segments.new', '/new', factory=factory)
    config.add_route('sales_segments.index', '/{event_id}', factory=factory)
    config.add_route('sales_segments.show', '/show/{sales_segment_id}', factory=factory)
    config.add_route('sales_segments.edit', '/edit/{sales_segment_id}', factory=factory)
    config.add_route('sales_segments.delete', '/delete/{sales_segment_id}', factory=factory)
    config.add_route('sales_segments.api.get_sales_segment_group_info', '/api/sales_segment_groups/{sales_segment_group_id}', factory=factory)
    config.add_route('sales_segments.point_grant_settings.add', '/{sales_segment_id}/point_grant_settings/add', factory=factory)
    config.add_route('sales_segments.point_grant_settings.remove', '/{sales_segment_id}/point_grant_settings/remove', factory=factory)
