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

    #####
    ## static route for demo page
    ##
    config.add_route("page_search_input", "/search/input", static=True)
    config.add_route("page_search_result", "/search/result/detail", static=True)
    config.add_route("page_search_by_freeword", "/searach/result/freeword", static=True)
    config.add_route("page_search_by_multi", "/searach/result/multi", static=True)
    config.add_route("page_search_by", "/searach/result/{kind}/{value}", static=True)

