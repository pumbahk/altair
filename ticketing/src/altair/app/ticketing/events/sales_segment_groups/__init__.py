# -*- coding: utf-8 -*-

def includeme(config):
    from .resources import SalesSegmentGroupAdminResource
    config.add_route('sales_segment_groups.index', '/{event_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.show', '/show/{sales_segment_group_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.new', '/new/{event_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.edit', '/edit/{sales_segment_group_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.delete', '/delete/{sales_segment_group_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.copy', '/copy/{sales_segment_group_id}', factory=SalesSegmentGroupAdminResource)
    config.add_route("sales_segment_groups.bind_membergroup",  "/bind/membergroup/{sales_segment_group_id}", factory=SalesSegmentGroupAdminResource)
    config.add_route("sales_segment_groups.lot_delete",  "/lot/delete/{lot_id}/{sales_segment_group_id}", factory=SalesSegmentGroupAdminResource)
    config.add_route('sales_segment_groups.copy_lot', '/copy/lot/{lot_id}', factory=SalesSegmentGroupAdminResource)
