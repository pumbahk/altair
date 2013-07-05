def includeme(config):
    config.add_route("staticpage", "s/{path:.*}")
