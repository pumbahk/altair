# coding: utf-8
def includeme(config):
    config.add_route('api_event_object', '/api/event/{id}')
    config.add_route('api_event', '/api/event/')
