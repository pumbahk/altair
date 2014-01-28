# -*- coding:utf-8 -*-
from altaircms.event.models import Event
from altaircms.page.models import Page
from altairsite.preview.api import set_rendered_event

class DetailPageResource(object):

    def __init__(self, request):
        self.request = request

    def get_event(self, id):
        event = self.request.allowable(Event).filter(Event.id==id).first()
        set_rendered_event(self.request, event)
        return event

    def get_page_published(self, event_id):
        page = self.request.allowable(Page).filter(Page.event_id==event_id).filter(Page.published==True).first()
        return page
