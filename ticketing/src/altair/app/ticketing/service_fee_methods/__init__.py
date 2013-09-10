# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('service_fee_methods.index', '/')
    config.add_route('service_fee_methods.new', '/new')
    config.add_route('service_fee_methods.edit', '/edit/{service_fee_method_id}')
    config.add_route('service_fee_methods.delete', '/delete/{service_fee_method_id}')
    config.scan(".")
