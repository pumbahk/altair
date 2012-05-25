def get_purchase_page_from_event(request, event):
    import warnings
    warnings.warn("this is ad-hoc. please fixme.  <detail-page> => <purchase flow>")
    return u"/cart/events/%d" % event.backend_id

def get_purchase_page_from_performance(request, event):
    import warnings
    warnings.warn("this is ad-hoc. please fixme.  <detail-page> => <purchase flow>")
    return 

def get_searchpage(request, kind=None, value=None):
    return request.route_path("page_search_by", kind=kind, value=value)

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
