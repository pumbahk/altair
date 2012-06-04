# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('delivery_methods.index', '/')
    config.add_route('delivery_methods.new', '/new')
    config.add_route('delivery_methods.edit', '/edit/{delivery_method_id}')
    config.add_route('delivery_methods.show', '/show/{delivery_method_id}')
    config.add_route('delivery_methods.delete', '/delete/{delivery_method_id}')
    config.scan(".")
