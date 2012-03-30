def includeme(config):
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')

    config.add_route('operator_list', '/operator/')
    config.add_route('operator', '/operator/{id}')

    config.add_route('role_list', '/role/')
    config.add_route('role', '/role/{id}')

    config.add_route('role_permission_list', '/role/{role_id}/permission/')
    config.add_route('role_permission', '/role/{role_id}/permission/{id}')
