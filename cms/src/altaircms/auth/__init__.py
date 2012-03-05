def includeme(config):
    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')

    config.add_route('operator_list', '/operator/')
    config.add_route('operator', '/operator/{id}')

    config.add_route('apikey_list', '/apikey/')
    config.add_route('apikey', '/apikey/{id}')

    config.add_route('role_list', '/role/')
    config.add_route('role', '/role/{id}')
