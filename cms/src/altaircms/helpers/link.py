def get_searchpage_from_category(request, category, kind=None, **kwargs):
    return request.route_path("page_search_by", kind=kind, _query=kwargs)

def get_link_from_category(request, category):
    if category.pageset is None:
        return category.url
    else:
        return to_publish_page_from_pageset(request, category.pageset)

def to_publish_page_from_pageset(request, pageset):
    url = pageset.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return request.route_path("front", page_name=url)
