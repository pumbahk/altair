# -*- coding:utf-8 -*-

def includeme(config):
    config.add_route('tickets.preview', '/preview')
    config.add_route("tickets.preview.download", '/preview/download')
    config.add_route("tickets.preview.combobox", '/preview/combobox')
    config.add_route("tickets.preview.api", "/api/preview/{action}")
    config.add_route("tickets.preview.combobox.api", "/api/preview/ombobox/{model}")
    config.scan(".views")

    settings = config.registry.settings
    ## svg preview serverとの通信
    from .api import SVGPreviewCommunication
    svg_preview_communication = SVGPreviewCommunication(
        settings["altair.preview.svg.post_url"], 
        )
    svg_preview_communication.bind_instance(config)

    ## sej preview serverとの通信
    from .api import SEJPreviewCommunication
    sej_preview_communication = SEJPreviewCommunication(
        settings["altair.preview.sej.post_url"], 
        )
    sej_preview_communication.bind_instance(config)
