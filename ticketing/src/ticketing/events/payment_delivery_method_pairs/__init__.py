# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('payment_delivery_method_pairs.new', '/{sales_segment_id}/new')
    config.add_route('payment_delivery_method_pairs.edit', '/edit/{payment_delivery_method_pair_id}/')
    config.add_route('payment_delivery_method_pairs.delete', '/delete/{payment_delivery_method_pair_id}/')
