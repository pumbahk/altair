# -*- coding: utf-8 -*-
from altaircms.solr import api as solrapi
from altaircms.event.models import Event
from altaircms.page.models import Page
from cmsmobile.core.helper import log_info

def searchEvents(request, word):
    log_info("searchEvents", "start")
    searcher = solrapi.get_fulltext_search(request)
    response = searcher.solr.select(word)
    events = getResultEvents(request, response)
    log_info("searchEvents", "end")
    return events

def getResultEvents(request, response):
    log_info("getResultEvents", "start")
    ids = [res['id'] for res in response]
    events = []
    log_info("getResultEvents", "freeword result id = " + str(ids))
    for page_id in ids:
        page = request.allowable(Page).filter(Page.id == page_id).first()
        if page:
            event = request.allowable(Event).filter(Event.id == page.event_id).first()
            if event:
                if not event in events:
                    log_info("getResultEvents", "event exist %d", event.id)
                    events.append(event)
    log_info("getResultEvents", "end")
    return events

