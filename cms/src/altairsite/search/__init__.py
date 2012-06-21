import functools
from ..mobile.custom_predicates import mobile_access_predicate

def includeme(config):
    add_route = functools.partial(config.add_route, factory=".resources.SearchPageResource")
    add_route("page_search_input", "/input") #input, result
    add_route("page_search_result", "/result/detail")
    add_route("page_search_by_freeword", "/result/freeword")
    add_route("page_search_by_multi", "/result/multi")
    add_route("page_search_by", "/result/{kind}/{value}")

    ## mobile
    config.add_view("altairsite.mobile.views.search_by_freeword", 
                    route_name="page_search_by_freeword", 
                    renderer="altaircms:templates/mobile/search.mako", 
                    custom_predicates=(mobile_access_predicate,))

    config.scan(".views")
    


