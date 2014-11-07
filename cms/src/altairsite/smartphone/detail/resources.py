# -*- coding:utf-8 -*-
from altaircms.event.models import Event
from altaircms.page.models import Page
from altairsite.preview.api import set_rendered_event
from altairsite.separation import get_organization_from_request


class DetailPageResource(object):

    def __init__(self, request):
        self.request = request

    def get_event(self, id):
        event = self.request.allowable(Event).filter(Event.id==id).first()
        set_rendered_event(self.request, event)
        return event

    def get_page_published(self, event_id, dt):
        page = (self.request.allowable(Page)
                .filter(Page.event_id == event_id)
                .filter(Page.published == True)
                .filter(Page.in_term(dt))
                ).first()
        return page

    def is_dynamic_page_organization(self):
        org = get_organization_from_request(request=self.request)
        return org.short_name == "KT"