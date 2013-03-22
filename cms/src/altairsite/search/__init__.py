import functools

def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.SearchPageResource")
    add_route("page_search_input", "/input") #input, result
    add_route("page_search_result", "/result/detail")
    add_route("page_search_by_freeword", "/result/freeword")
    add_route("page_search_by_multi", "/result/multi")
    add_route("page_search_by", "/result/{kind}/{value}")

    ## mobile
    for route_name in ["page_search_input", 
                       "page_search_result", 
                       "page_search_by_freeword", 
                       "page_search_by_multi", 
                       "page_search_by"]:
        config.add_view("altairsite.mobile.dispatch.views.dispatch_view", 
                        route_name=route_name, 
                        request_type="altairsite.mobile.tweens.IMobileRequest")
    config.scan(".views")
    


