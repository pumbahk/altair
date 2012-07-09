# -*- coding:utf-8 -*-

from altaircms.event.models import Event
from altaircms.page.models import Page
from altaircms.page.models import PageSet

def get_event(request):
    if hasattr(request, "_event"):
        return request._event
    else:
        event_id = request.session.get("event_id", None)
        event = request.allowable(Event).filter_by(id=event_id).first()
        set_event(request, event)
        return event

def get_page(request):
    if hasattr(request, "_page"):
        return request._page
    else:
        page_id = request.session.get("page_id", None)
        page = request.allowable(Page).filter_by(id=page_id).first()
        set_page(request, page)
        return page

def get_pageset(request):
    if hasattr(request, "_pageset"):
        return request._pageset
    else:
        pageset_id = request.session.get("pageset_id", None)
        pageset = request.allowable(PageSet).filter_by(id=pageset_id).first()
        set_pageset(request, pageset)
        return pageset

def get_tags(request):
    if hasattr(request, "_tags"):
        return request._tags
    page = get_page(request)
    if page:
        return page.tags
    else:
        return []

def get_hotwords(request):
    if hasattr(request, "_hotwords"):
        return request._hotwords
    tags = get_tags(request)
    if tags:
        return [word for tag in tags for word in tag.hotwords]
    else:
        return []

def get_accesskeys(request):
    if hasattr(request, "_accesskeys"):
        return request._accesskeys
    page = get_page(request)
    accesskeys = page.access_keys
    set_accesskeys(request)
    return accesskeys

def get_pagesets(request):
    if hasattr(request, "_pagesets"):
        return request._pagesets
    event = get_event(request)
    if event:
        return event.pagesets
    else:
        return []

def get_performances(request):
    if hasattr(request, "_performances"):
        return request._performances
    event = get_event(request)
    if event:
        return event.performances
    else:
        return []

def get_sales(request):
    if hasattr(request, "_sales"):
        return request._sales
    event = get_event(request)
    if event:
        return event.sales
    else:
        return []

def get_assets(request):
    if hasattr(request, "_assets"):
        return request._assets
    raise NotImplemented

def get_topics(request):
    if hasattr(request, "_topics"):
        return request._topics
    raise NotImplemented

def get_topcontents(request):
    if hasattr(request, "_topcontents"):
        return request._topcontents
    raise NotImplemented
    
def set_event(request, event):
    request._event = event

def set_page(request, page):
    request._page = page

def set_pagesets(request, pagesets):
    request._pagesets = pagesets

def set_pageset(request, pageset):
    request._pageset = pageset

def set_tags(request, tags):
    request._tags = tags

def set_hotwords(request, hotwords):
    request._hotwords = hotwords

def set_accesskeys(request, accesskeys):
    request._accesskeys = accesskeys

def set_performances(request, performances):
    request._performances = performances

def set_sales(request, sales):
    request._sales = sales

def set_assets(request, assets):
    request._assets = assets

def set_topics(request, topics):
    request._topics = topics

def set_topcontents(request, topcontents):
    request._topcontents = topcontents
