# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('payment_delivery_method_pairs.new', '/new/{sales_segment_group_id}')
    config.add_route('payment_delivery_method_pairs.edit', '/edit/{payment_delivery_method_pair_id}/')
    config.add_route('payment_delivery_method_pairs.delete', '/delete/{payment_delivery_method_pair_id}/')
    config.add_route('payment_delivery_method_pairs.default_values_for_pdmp', '/default_values_for_pdmp')
