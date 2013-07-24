def includeme(config):
    config.add_route("staticpage", "s/{page_name:.*}")
