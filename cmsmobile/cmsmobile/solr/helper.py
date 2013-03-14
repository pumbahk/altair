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
        print page_id
        page = request.allowable(Page).filter(Page.id == page_id).first()
        if page:
            event = request.allowable(Event).filter(Event.id == page.event_id).first()
            if event:
                if not event in events:
                    events.append(event)
    log_info("getResultEvets", "end")
    return events

