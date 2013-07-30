def includeme(config):
    config.add_route("staticpage", "s/{page_name:.*}")
    config.add_route("mobile.features", "features/{page_name:.*}")
