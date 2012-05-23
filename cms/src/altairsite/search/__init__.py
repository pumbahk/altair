def includeme(config):
    config.add_route("page_search_input", "/search/input", factory=".resources.SearchPageResource") #input, result
    config.add_route("page_search_result", "/search/result", factory=".resources.SearchPageResource")
    config.scan(".views")
    


