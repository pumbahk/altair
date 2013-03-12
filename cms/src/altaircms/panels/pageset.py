import sqlalchemy as sa
from datetime import datetime
from altaircms.page.models import PageType

def nav_pageset_panel(context, request, pagetype):
    pagetypes = request.allowable(PageType).all()
    pagetype_id = unicode(pagetype.id)
    candidates = []
    for pt in pagetypes:
        if unicode(pt.id) == pagetype_id:
            candidates.append(("active", pt))
        else:
            candidates.append(("", pt))
    return {"pagetypes": candidates}
        
def pageset_page_listing_panel(context, request, pageset):
    now = datetime.now()
    pages = pageset.pages
    current_page = pageset.current(now, published=True)
    return dict(pageset=pageset, 
                pages=pages, 
                now=now, 
                current_page=current_page)
