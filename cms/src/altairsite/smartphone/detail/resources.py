# -*- coding:utf-8 -*-
from altaircms.event.models import Event
from altairsite.preview.api import set_rendered_event

class DetailPageResource(object):
    def __init__(self, request):
        self.request = request
    def get_event(self, id):
        event = self.request.allowable(Event).filter(Event.id==id).first()
        set_rendered_event(self.request, event)
        return event
