def includeme(config):
    config.add_route('tickets.preview', '/preview')
    config.add_route("tickets.preview.download", '/preview/download')
    config.add_route("tickets.preview.combobox", '/preview/combobox')
    config.add_route("tickets.preview.api", "/api/preview/{action}")
    config.add_route("tickets.preview.combobox.api", "/api/preview/ombobox/{model}")
    config.scan(".views")
