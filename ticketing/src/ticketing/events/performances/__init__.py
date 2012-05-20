# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('performances.index', '/{event_id}/performances')
    config.add_route('performances.new', '/{event_id}/performances/new')
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')
