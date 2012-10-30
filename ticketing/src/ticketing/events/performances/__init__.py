# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('performances.index', '/{event_id}')
    config.add_route('performances.new', '/new/{event_id}')
    config.add_route('performances.show', '/show/{performance_id}')
    config.add_route('performances.show_tab', '/show/{performance_id}/{tab}')
    config.add_route('performances.edit', '/edit/{performance_id}')
    config.add_route('performances.delete', '/delete/{performance_id}')
    config.add_route('performances.copy', '/copy/{performance_id}')
    config.add_route('performances.open', '/open/{performance_id}')
    config.add_route("performances.mailinfo.index", "/mailinfo/{performance_id}")
    config.add_route("performances.mailinfo.edit", "/mailinfo/{performance_id}/mailtype/{mailtype}")
