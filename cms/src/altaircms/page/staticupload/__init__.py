def includeme(config):
    from .api import set_static_page_utility
    config.add_route("static_pageset", "/page/pagetype/{pagetype}/{static_page_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_create", "/page/pagetype/{pagetype}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page", "/page/static/{static_page_id}/unit/{child_id}/{action}",factory=".resources.StaticPageResource") 
    config.add_route("static_page_display", "/page/static/display/{path:.*}",factory=".resources.StaticPageResource")
    settings = config.registry.settings
    set_static_page_utility(
        config, 
        settings["altaircms.page.static.directory"], 
        settings["altaircms.page.tmp.directory"]
        )

    config.add_route("static_page_part_file", "/page/static/{static_page_id}/unit/{child_id}/file/{path}/{action}", factory=".resources.StaticPageResource")
    config.add_route("static_page_part_directory", "/page/static/{static_page_id}/unit/{child_id}/file/{path}/{action}", factory=".resources.StaticPageResource")
    config.scan(".views")

