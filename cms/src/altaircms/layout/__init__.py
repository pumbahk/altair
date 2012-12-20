# coding: utf-8

def includeme(config):
    """
    altaircms.layout_directory = altaircms:templates/front/layout
    """
    from .api import register_layout_creator
    register_layout_creator(config, config.registry.settings["altaircms.layout_directory"])

    config.add_route('layout_demo', '/demo/layout/')
    config.add_route("layout_preview", "/layout/{layout_id}/preview")
    config.add_route("layout_download", '/layout/{layout_id}/download')
    config.add_route("layout_create", "/layout/create/{action}")
    ## bind event
    config.add_subscriber(".subscribers.create_template_layout", ".subscribers.LayoutCreate")
    config.scan(".views")
