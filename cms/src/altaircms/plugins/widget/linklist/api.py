from zope.interface import implementer
import sqlalchemy as sa
from .interfaces import IWFinder
from altaircms.models import DBSession
from altaircms.event.models import Event
from altaircms.page.models import PageSet
import altaircms.helpers as h

def get_linklist_candidates_finder(request, key):
    return request.registry.getUtility(IWFinder, key)

@implementer(IWFinder)
class Finderize(object):
    def __init__(self, finder):
        self.find = finder

## fixme. if slow query
def _near_the_end_events(request, N, today, max_items=None):
    qs = DBSession.query(PageSet.name, PageSet.url).filter(PageSet.event_id==Event.id)
    qs =  Event.near_the_deal_close_query(today, N=N, qs=qs)
    qs = qs.order_by(sa.asc(Event.deal_close))
    if max_items:
        qs = qs.limit(max_items)
    return [u'<a href="%s">%s</a>' % (h.front.to_publish_page_from_pageset(request, p), p.name) for p in qs]
near_the_end_events = Finderize(_near_the_end_events)

def _deal_start_this_week_events(request, N, today, max_items=None):
    qs = DBSession.query(PageSet.name, PageSet.url).filter(PageSet.event_id==Event.id)
    qs =  Event.deal_start_this_week_query(today, offset=-today.weekday(), qs=qs)
    qs = qs.order_by(sa.desc(Event.deal_open))
    if max_items:
        qs = qs.limit(max_items)
    return [u'<a href="%s">%s</a>' % (h.front.to_publish_page_from_pageset(request, p), p.name) for p in qs]
deal_start_this_week_events = Finderize(_deal_start_this_week_events)
