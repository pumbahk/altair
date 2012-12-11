def includeme(config):
    config.add_route('tickets.preview', '/preview')
    config.add_route("tickets.preview.combobox", '/preview/combobox')
    config.add_route("tickets.preview.api", "/api/preview/{action}")
    config.add_route("tickets.preview.combobox.api", "/api/preview/combobox/{model}")
    config.scan(".views")
