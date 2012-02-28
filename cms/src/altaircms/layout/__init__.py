# coding: utf-8

def includeme(config):
    config.add_route('api_layout_object', '/api/layout/{id}')
    config.add_route('api_layout', '/api/layout/')
