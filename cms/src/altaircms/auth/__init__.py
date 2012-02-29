def includeme(config):
    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')

    config.add_route('operator_list', '/operator/')
    config.add_route('operator', '/operator/{id}')
