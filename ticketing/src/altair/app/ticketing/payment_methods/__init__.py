# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('payment_methods.index', '/')
    config.add_route('payment_methods.new', '/new')
    config.add_route('payment_methods.edit', '/edit/{payment_method_id}')
    config.add_route('payment_methods.delete', '/delete/{payment_method_id}')
    config.scan(".")
