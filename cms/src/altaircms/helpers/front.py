def to_preview_page(request, page):
    return request.route_url("front_preview", page_name=page.hash_url)
