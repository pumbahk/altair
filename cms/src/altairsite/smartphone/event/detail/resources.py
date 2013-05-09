# -*- coding:utf-8 -*-
from altairsite.smartphone.resources import TopPageResource
from altaircms.event.models import Event

class DetailPageResource(object):
    def __init__(self, request):
        self.request = request
    def get_event(self, id):
        event = self.request.allowable(Event).filter(Event.id==id).first()
        return event
