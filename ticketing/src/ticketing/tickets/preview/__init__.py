def includeme(config):
    config.add_route('tickets.preview', '/preview')
    config.add_route("tickets.preview.api", "/api/preview/{action}")
    config.scan(".views")
