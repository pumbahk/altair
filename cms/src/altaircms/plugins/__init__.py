def includeme(config):
    config.include(".widget.image", route_prefix="api")
    config.include(".widget.freetext", route_prefix="api")
    config.include(".widget.flash", route_prefix="api")
    config.include(".widget.movie", route_prefix="api")
    config.include(".widget.calendar", route_prefix="api")
    config.include(".widget.performancelist", route_prefix="api")
    config.include(".widget.detail", route_prefix="api")
    config.include(".widget.ticketlist", route_prefix="api")
    config.include(".widget.menu", route_prefix="api")


