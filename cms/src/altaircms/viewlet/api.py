# -*- coding:utf-8 -*-

from altaircms.event.models import Event
from altaircms.page.models import Page

def get_event(request):
    if hasattr(request, "_event"):
        return request._event
    else:
        event_id = request.session.get("event_id", None)
        event = Event.query.filter_by(id=event_id).first()
        set_event(request, event)
        return event

def get_page(request):
    if hasattr(request, "_page"):
        return request._page
    else:
        page_id = request.session.get("page_id", None)
        page = Page.query.filter_by(id=page_id).first()
        set_page(request, page)
        return page

def get_tags(request):
    if hasattr(request, "_tags"):
        return request._tags
    page = get_page(request)
    if page:
        return page.tags
    else:
        return []

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
    
def set_event(request, event):
    request._event = event

def set_page(request, page):
    request._page = page

def set_pagesets(request, pagesets):
    request._pagesets = pagesets

def set_tags(request, tags):
    request._tags = tags

def set_performances(request, performances):
    request._performances = performances

def set_sales(request, sales):
    request._sales = sales

    
