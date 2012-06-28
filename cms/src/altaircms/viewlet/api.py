# -*- coding:utf-8 -*-

from altaircms.event.models import Event

def get_event(request):
    if hasattr(request, "_event"):
        return request._event
    else:
        event_id = request.session.get("event_id", None)
        event = Event.query.filter_by(id=event_id).first()
        set_event(request, event)
        return event

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

def set_pagesets(request, pagesets):
    request._pagesets = pagesets

def set_performances(request, performances):
    request._performances = performances

def set_sales(request, sales):
    request._sales = sales

    
