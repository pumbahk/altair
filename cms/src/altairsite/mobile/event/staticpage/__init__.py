def includeme(config):
    config.add_route("staticpage", "staticpage/{path:.*}")
