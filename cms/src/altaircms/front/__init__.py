def includeme(config):
    settings = config.registry.settings
    from altairsite.front.resolver import LayoutModelResolver
    from altairsite.front.resolver import ILayoutModelResolver
    layout_lookup = LayoutModelResolver(settings["altaircms.layout_directory"],
                                   checkskip=True)
    config.registry.registerUtility(layout_lookup, ILayoutModelResolver)
    config.add_directive("set_lookup_wrapper", "altairsite.front.install_lookupwrapper")
    config.set_lookup_wrapper(name="intercept", sync_trigger_attribute_name="uploaded_at")
    config.add_route("preview_pageset", "/preview/pageset/{pageset_id}", factory=".resources.PageRenderingResource")
    config.add_route("preview_page", "/preview/page/{page_id}", factory=".resources.PageRenderingResource")
    config.scan(".views")


    #####
    ## static route for demo page
    ##
    config.add_route("front", "/publish/{page_name:.*}")
    config.add_route("page_search_input", "/search/input", static=True)
    config.add_route("page_search_result", "/search/result/detail", static=True)
    config.add_route("page_search_by_freeword", "/search/result/freeword", static=True)
    config.add_route("page_search_by_multi", "/search/result/multi", static=True)
    config.add_route("page_search_by", "/search/result/{kind}/{value}", static=True)

