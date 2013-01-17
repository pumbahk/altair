# -*- coding:utf-8 -*-

class TicketPreviewException(Exception):
    pass

class TicketPreviewFillValuesException(TicketPreviewException):
    pass
class TicketPreviewTransformException(TicketPreviewException):
    pass
class TicketPreviewAPIException(TicketPreviewException):
    pass

def include_views(config):
    config.add_route('tickets.preview', '/preview')
    config.add_route('tickets.preview.dialog', '/preview/dialog/{model}')
    config.add_route("tickets.preview.download", '/preview/download')
    config.add_route("tickets.preview.enqueue", '/preview/enqueue')
    config.add_route("tickets.preview.combobox", '/preview/combobox')
    config.add_route("tickets.preview.api", "/api/preview/{action}")
    config.add_route("tickets.preview.combobox.api", "/api/preview/combobox/{model}")
    config.add_route("tickets.preview.loadsvg.api", "/api/preview/loadsvg/{model}")
    config.scan(".views")

def include_utilities(config):
    settings = config.registry.settings
    ## svg preview serverとの通信
    from .api import SVGPreviewCommunication
    svg_preview_communication = SVGPreviewCommunication(
        settings["altair.preview.svg.post_url"]
        )
    svg_preview_communication.bind_instance(config)

    ## sej preview serverとの通信
    from .api import SEJPreviewCommunication
    sej_preview_communication = SEJPreviewCommunication(
        settings["altair.preview.sej.post_url"]
        )
    sej_preview_communication.bind_instance(config)

def includeme(config):
    config.include(include_views)
    config.include(include_utilities)
