# coding: utf-8

def includeme(config):
    config.add_route('layout', '/layout/{layout_id}')
    config.add_route('layout_list', '/layout/')
    ## api
    config.add_route('api_layout_object', '/api/layout/{id}')
    config.add_route('api_layout', '/api/layout/')
