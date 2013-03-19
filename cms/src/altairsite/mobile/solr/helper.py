# -*- coding: utf-8 -*-
from altaircms.solr import api as solrapi
from altaircms.event.models import Event
from altaircms.page.models import PageSet
from altairsite.mobile.core.helper import log_info

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
    log_info("getResultEvents", "freeword result pageset_ids = " + str(ids))
    for pageset_id in ids:
        pageset = request.allowable(PageSet).filter(PageSet.id == pageset_id).first()
        if pageset:
            log_info("getResultEvents", "pageset_id = " + str(pageset_id) + " exist")
            event = request.allowable(Event).filter(Event.id == pageset.event_id).first()
            if event:
                if not event in events:
                    events.append(event)
    log_info("getResultEvents", "end")
    return events

