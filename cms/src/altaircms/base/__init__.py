def includeme(config):
    config.add_route("apikey_list", "/apikey/")
    config.add_route("apikey", "/apikey/{id}")
