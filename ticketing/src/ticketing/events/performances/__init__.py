# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')

    config.add_route('stock_holders.new', '/{performance_id}/stock_holders/new')
    config.add_route('stock_holders.edit', '/stock_holders/edit/{stock_holder_id}')
    config.add_route('stock_holders.delete', '/stock_holders/delete/{stock_holder_id}')
