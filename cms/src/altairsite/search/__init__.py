def includeme(config):
    config.add_route("page_search_input", "/input", factory=".resources.SearchPageResource") #input, result
    config.add_route("page_search_result", "/result/detail",  factory=".resources.SearchPageResource")
    config.add_route("page_search_by_freeword", "/result/freeword",  factory=".resources.SearchPageResource")
    config.add_route("page_search_by_multi", "/result/multi",  factory=".resources.SearchPageResource")
    config.add_route("page_search_by", "/result/{kind}/{value}",  factory=".resources.SearchPageResource")
    config.scan(".views")
    


