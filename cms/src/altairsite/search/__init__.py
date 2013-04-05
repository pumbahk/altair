import functools

def includeme(config):
    from altaircms.page.models import PageTag
    def get_page_tag_factory(request):
        def _(labelname):
            return request.allowable(PageTag).filter_by(label=labelname, publicp=True).first()
        return _
    config.set_request_property(get_page_tag_factory,  "get_page_tag", reify=True)

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
    


