# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('sales_segments.new', '/new')
    config.add_route('sales_segments.edit', '/edit/{sales_segment_id}')
    config.add_route('sales_segments.delete', '/delete/{sales_segment_id}')
    config.add_route('sales_segments.api.get_payment_delivery_method_pairs', '/api/pdmp/')
