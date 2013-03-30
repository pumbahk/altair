def includeme(config):
    settings = config.registry.settings
    layout_lookup_class = config.maybe_dotted("altairsite.front.impl.LayoutTemplate")
    layout_lookup = layout_lookup_class(settings["altaircms.layout_directory"])
    config.registry.registerUtility(layout_lookup, config.maybe_dotted("altairsite.front.impl.ILayoutTemplateLookUp"))

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

