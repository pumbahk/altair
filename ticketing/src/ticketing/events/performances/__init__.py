# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')

    config.add_route('performances.stock_holder.new', '/{performance_id}/stock_holder/new')
