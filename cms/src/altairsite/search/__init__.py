import functools
def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.SearchPageResource")
    add_route("page_search_input", "/input") #input, result
    add_route("page_search_result", "/result/detail")
    add_route("page_search_by_freeword", "/result/freeword")
    add_route("page_search_by_multi", "/result/multi")
    add_route("page_search_by", "/result/{kind}/{value}")

    ## mobile
    add_route("mobile_page_search", "/m/result")
    config.scan(".views")
    


