from zope.interface import provider
import sqlalchemy as sa
from .interfaces import IWFinder
import sqlalchemy.orm as orm
from altaircms.event.models import Event
from altaircms.page.models import PageSet, Page


def get_linklist_candidates_finder(request, key):
    return request.registry.getUtility(IWFinder, key)

@provider(IWFinder)
def near_the_end_events(request, N, today):
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(today))
    qs = qs.join(Page, Page.pageset_id == PageSet.id)
    qs = qs.filter(Page.published == True)
    # XXX: この条件だと、当日の 0:00:00 以降に公開になったページが対象に含まれなくなってしまうので、today より now がほしい
    qs = qs.filter(Page.publish_begin < today)
    qs = qs.filter((Page.publish_end==None) | (Page.publish_end > today))
    qs = qs.filter(Event.is_searchable==True)
    qs = Event.near_the_deal_close_query(today, N=N, qs=qs)
    qs = qs.order_by(sa.asc(Event.deal_close)).options(orm.joinedload(PageSet.event)).distinct(PageSet.id)
    return qs

@provider(IWFinder)
def deal_start_this_week_events(request, N, today):
    qs = request.allowable(PageSet).filter(PageSet.event_id==Event.id, PageSet.id==Page.pageset_id, Page.in_term(today))
    qs = qs.join(Page, Page.pageset_id == PageSet.id)
    qs = qs.filter(Page.published == True)
    # XXX: この条件だと、当日の 0:00:00 以降に公開になったページが対象に含まれなくなってしまうので、today より now がほしい
    qs = qs.filter(Page.publish_begin < today)
    qs = qs.filter((Page.publish_end==None) | (Page.publish_end > today))
    qs = qs.filter(Event.is_searchable==True)
    qs =  Event.deal_start_this_week_query(today, offset=-today.weekday(), qs=qs)
    qs = qs.order_by(sa.desc(Event.deal_open)).options(orm.joinedload(PageSet.event)).distinct(PageSet.id)
    return qs           
