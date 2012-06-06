def includeme(config):
    if config.registry.settings.get("altaircms.usersite.url") is None: 
        import warnings
        warnings.warn("altaircms.usersite.url is not found; defaulting to http://localhost:5432")
        config.registry.settings["altaircms.usersite.url"] = "http://localhost:5432"

    config.add_route('front', '/publish/{page_name:.*}') # fix-url after. implemnt preview
    config.add_route("front_to_preview", "/to/preview/{page_id}")
    config.add_route("front_preview_pageset", "/preview/pageset/{pageset_id}")
    config.add_route('front_preview', '/preview/{page_id}/{page_name:.*}', factory="altairsite.front.resources.PageRenderingResource")

    config.scan('.views')
    config.scan("altairsite.front.views")
