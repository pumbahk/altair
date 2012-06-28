# -*- coding:utf-8 -*-

from ..models import Event

def get_event(request):
    if hasattr(request, "_event"):
        return request._event
    else:
        event_id = request.session.get("event_id", None)
        event = Event.query.filter_by(id=event_id).first()
        set_event(request, event)
        return event

def set_event(request, event):
    request._event = event

    
