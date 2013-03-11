# -*- coding: utf-8 -*-
from altaircms.solr import api as solrapi
from altaircms.event.models import Event
from altaircms.page.models import Page
from cmsmobile.core.helper import log_info

def searchEvents(request, word):
    log_info("searchEvents", "start")
    searcher = solrapi.get_fulltext_search(request)
    response = searcher.solr.select(word)
    events = getResultEvets(request, response)
    log_info("searchEvents", "end")
    return events

def getResultEvets(request, response):
    log_info("getResultEvets", "start")
    ids = [res['id'] for res in response]
    events = []
    for page_id in ids:
        page = Page.query.filter(Page.id == page_id) \
            .filter(Page.organization_id == request.organization.id).first()
        if page:
            event = Event.query.filter(Event.id == page.event_id) \
                .filter(Event.organization_id == request.organization.id).first()
            if event:
                if not event in events:
                    events.append(event)
    log_info("getResultEvets", "end")
    return events

