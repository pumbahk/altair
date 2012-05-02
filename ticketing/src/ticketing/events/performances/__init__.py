# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('performances.new', '/{event_id}/new')
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')
    config.add_route('performances.stock_holder.new', '/stock_holder/{performance_id}/new')
