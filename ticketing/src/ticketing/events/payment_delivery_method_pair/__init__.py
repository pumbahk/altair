# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('payment_delivery_method_pair.edit', '/edit/{payment_delivery_method_pair_id}/')
    config.add_route('payment_delivery_method_pair.delete', '/delete/{payment_delivery_method_pair_id}/')
