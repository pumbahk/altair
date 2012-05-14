def includeme(config):
    config.add_route("detail_page_search_input", "/detail/input") #input, result
    config.add_route("detail_page_search", "/detail/result") #input, result
    config.add_route("page_search", "/result")
    config.scan(".views")
    


