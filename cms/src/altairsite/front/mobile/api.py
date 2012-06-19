import sqlalchemy as sa
from altaircms.models import Category
from altaircms.event.models import Event
from altaircms.page.models import PageSet
from .helpers import CATEGORY_SYNONYM


def events_on_sale_this_week(request, category_origin, today):
    qs = PageSet.query.filter(PageSet.event_id==Event.id)
    qs = qs.filter(Event.is_searchable==True)
    qs =  Event.deal_start_this_week_query(today, offset=-today.weekday(), qs=qs)
    qs = qs.order_by(sa.desc(Event.deal_open))
    return qs.filter(PageSet.id==Category.pageset_id).filter(Category.origin==category_origin)

def url_from_category(request, category):
    return request.route_path("mobile_category", category=category.name)

def category_to_breadcrumbs(request, category, word, url_from_category=url_from_category):
    cands = category.ancestors(include_self=True)
    breadcrumbs = reversed([u'<a href="%s">%s</a>' % (url_from_category(request, c), CATEGORY_SYNONYM.get(c.name, c.label)) for c in cands])
    return breadcrumbs

