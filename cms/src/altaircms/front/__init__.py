def includeme(config):
    if config.registry.settings.get("altaircms.usersite.url") is None: 
        import warnings
        warnings.warn("altaircms.usersite.url is not found; defaulting to http://localhost:5432")
        config.registry.settings["altaircms.usersite.url"] = "http://localhost:5432"

    config.include("altairsite.front")
    config.add_route("rendering_pageset", "/preview/pageset/{pageset_id}")
    config.scan(".views")

    #####
    ## static route for demo page
    ##
    config.add_route("page_search_input", "/search/input", static=True)
    config.add_route("page_search_result", "/search/result/detail", static=True)
    config.add_route("page_search_by_freeword", "/searach/result/freeword", static=True)
    config.add_route("page_search_by_multi", "/searach/result/multi", static=True)
    config.add_route("page_search_by", "/searach/result/{kind}/{value}", static=True)

