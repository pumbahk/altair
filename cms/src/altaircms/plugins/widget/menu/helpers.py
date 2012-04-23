import json
import altaircms.helpers as h

to_publish_page = h.front.to_publish_page_from_pageset

def items_from_page(request, page, to_url=to_publish_page):
    return json.dumps( [{"label": p.name, "link": to_url(request, p)} \
                            for p in page.event.pagesets])        

