# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('sales_segments.index', '/{event_id}')
    config.add_route('sales_segments.show', '/show/{sales_segment_id}')
    config.add_route('sales_segments.new', '/new/{event_id}')
    config.add_route('sales_segments.edit', '/edit/{sales_segment_id}')
    config.add_route('sales_segments.delete', '/delete/{sales_segment_id}')
    config.add_route('sales_segments.copy', '/copy/{sales_segment_id}')
