# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('sales_segments.show', '/show/{sales_segment_id}')
    config.add_route('sales_segments.edit', '/edit/{sales_segment_id}')
    config.add_route('sales_segments.delete', '/delete/{sales_segment_id}')

    config.add_route('payment_delivery_method_pair.new', '/{sales_segment_id}/payment_delivery_method_pair/new')
