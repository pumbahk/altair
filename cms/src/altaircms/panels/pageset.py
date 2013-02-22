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
        
