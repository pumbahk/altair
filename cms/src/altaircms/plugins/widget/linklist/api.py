from zope.interface import provider
from datetime import datetime
import sqlalchemy as sa
from .interfaces import IWFinder
import sqlalchemy.orm as orm
from altaircms.event.models import Event
from altaircms.page.models import PageSet, Page


def get_linklist_candidates_finder(request, key):
    return request.registry.getUtility(IWFinder, key)

@provider(IWFinder)
def near_the_end_events(request, N, now):
    today = datetime(now.year, now.month, now.day)
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(now))
    qs = qs.join(Page, Page.pageset_id == PageSet.id)
    qs = qs.filter(Page.published == True)
    qs = qs.filter(Event.is_searchable==True)
    qs = Event.near_the_deal_close_query(today, N=N, qs=qs)
    qs = qs.order_by(sa.asc(Event.deal_close)).options(orm.joinedload(PageSet.event)).distinct(PageSet.id)
    return qs

@provider(IWFinder)
def deal_start_this_week_events(request, N, now):
    today = datetime(now.year, now.month, now.day)
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(now))
    qs = qs.join(Page, Page.pageset_id == PageSet.id)
    qs = qs.filter(Page.published == True)
    qs = qs.filter(Event.is_searchable==True)
    qs = Event.deal_start_this_week_query(today, offset=-today.weekday(), qs=qs)
    qs = qs.order_by(sa.desc(Event.deal_open)).options(orm.joinedload(PageSet.event)).distinct(PageSet.id)
    return qs           
