def includeme(config):
    config.add_route("page_search_input", "/search/input", factory=".resources.SearchPageResource") #input, result
    config.add_route("page_search_result", "/search/result/detail",  factory=".resources.SearchPageResource")
    config.add_route("page_search_by", "/searach/result/{kind}",  factory=".resources.SearchPageResource")
    config.scan(".views")
    


