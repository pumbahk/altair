
def get_link_from_category(request, category):
    if category.pageset is None:
        return category.url
    else:
        return to_publish_page_from_pageset(request, category.pageset)

def to_publish_page_from_pageset(request, pageset):
    return request.route_path("front", page_name=pageset.url)
