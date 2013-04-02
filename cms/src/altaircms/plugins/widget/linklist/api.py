from zope.interface import provider
import sqlalchemy as sa
from .interfaces import IWFinder
from altaircms.event.models import Event
from altaircms.page.models import PageSet, Page

def get_linklist_candidates_finder(request, key):
    return request.registry.getUtility(IWFinder, key)

@provider(IWFinder)
def near_the_end_events(request, N, today):
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(today))
    qs = qs.filter(Event.is_searchable==True)
    qs = Event.near_the_deal_close_query(today, N=N, qs=qs)
    qs = qs.order_by(sa.asc(Event.deal_close)).distinct(PageSet.id)
    return qs

@provider(IWFinder)
def deal_start_this_week_events(request, N, today):
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(today))
    qs = qs.filter(Event.is_searchable==True)
    qs =  Event.deal_start_this_week_query(today, offset=-today.weekday(), qs=qs)
    qs = qs.order_by(sa.desc(Event.deal_open)).distinct(PageSet.id)
    return qs           
