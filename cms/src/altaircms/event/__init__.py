
def includeme(config):
    config.add_route('api_event', '/api/event/')
    config.add_route('api_event_object', '/api/event/{id}')
