# -*- coding: utf-8 -*-

def includeme(config):
    config.add_route('announce.index', '/')
    config.add_route('announce.list', '/event/{event_id}')
    config.add_route('announce.new', '/event/{event_id}/new')
    config.add_route('announce.edit', '/edit/{announce_id}')
    config.add_route('announce.count', '/count')
    config.scan(".")
