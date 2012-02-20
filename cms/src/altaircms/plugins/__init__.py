def includeme(config):
    config.include(".widget.image", route_prefix="api")
    config.include(".widget.freetext", route_prefix="api")

