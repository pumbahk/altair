def includeme(config):
    config.add_route('oauth_entry', '/oauth')
    config.add_route('oauth_callback', '/oauth_callback')
