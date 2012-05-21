def includeme(config):
    config.add_route("detail_page_search_input", "/detail/input", factory=".resources.SearchPageResource") #input, result
    config.add_route("detail_page_search", "/detail/result", factory=".resources.SearchPageResource") #input, result
    config.add_route("page_search", "/result", factory=".resources.SearchPageResource")
    config.scan(".views")
    


