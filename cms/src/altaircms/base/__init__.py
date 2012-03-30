# coding: utf-8

def includeme(config):
    config.add_route('dashboard', '/')
    config.add_route('apikey_list', '/apikey/')
    config.add_route('apikey', '/apikey/{id}')

