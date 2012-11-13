# coding: utf-8

def includeme(config):
    """
    altaircms.layout_directory = altaircms:templates/front/layout
    """
    creator_class = config.maybe_dotted(".api.LayoutCreator")
    creator = creator_class(config.registry.settings["altaircms.layout_directory"])
    config.registry.registerUtility(creator, config.maybe_dotted(".interfaces.ILayoutCreator"))

    config.add_route('layout_demo', '/demo/layout/')
    config.add_route("layout_preview", "/layout/{layout_id}/preview")
    config.add_route("layout_download", '/layout/{layout_id}/download')
    config.add_route("layout_create", "/layout/create/{action}")
    ## bind event
    config.add_subscriber(".subscribers.create_template_layout", ".subscribers.LayoutCreate")
    config.scan(".views")
