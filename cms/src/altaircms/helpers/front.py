def to_preview_page(request, page):
    return request.route_path("front_preview", page_name=page.hash_url)

def to_publish_page(request, page):
    return request.route_path("front", page_name=page.url)
