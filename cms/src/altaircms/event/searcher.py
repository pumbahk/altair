from .models import Event
from .helpers import pageset_id_list_from_word
from ..page.models import PageSet
from ..models import Category

def _op_choice(x, sop, y):
    if sop == "lte":
        return x <= y
    elif sop == "eq":
        return x == y
    elif sop == "gte":
        return x >= y
    raise ValueError("invalid operator")

def make_event_search_query(request, data, qs=None):
    qs = qs or Event.query    
    qs = make_event_search_by_date(qs, data)    
    qs = make_event_search_by_word(request, qs, data)
    qs = make_event_search_by_category(qs, data)
    if data["is_vetoed"]:
        qs = qs.filter_by(is_searchable=False)
    return qs

def make_event_search_by_date(qs, data):
    if data["event_open"]:
        qs = qs.filter(_op_choice(Event.event_open, data["event_open_op"], data["event_open"]))
    if data["event_close"]:
        qs = qs.filter(_op_choice(Event.event_close, data["event_close_op"], data["event_close"]))
    if data["deal_open"]:
        qs = qs.filter(_op_choice(Event.deal_open, data["deal_open_op"], data["deal_open"]))
    if data["deal_close"]:
        qs = qs.filter(_op_choice(Event.deal_close, data["deal_close_op"], data["deal_close"]))
    if data["created_at"]:
        qs = qs.filter(_op_choice(Event.created_at, data["created_at_op"], data["created_at"]))
    if data["updated_at"]:
        qs = qs.filter(_op_choice(Event.updated_at, data["updated_at_op"], data["updated_at"]))
    return qs

def make_event_search_by_word(request, qs, data):
    ## search by solr
    if data["freeword"]:
        word = data["freeword"]
        pagesets = pageset_id_list_from_word(request, word)
        where = (Event.id==PageSet.event_id) & (PageSet.id.in_(pagesets))
        qs = qs.filter(where)
        # qs = qs.filter(where | Event.title.like(likeword), Event.subtitle.like(likeword))
    return qs


def make_event_search_by_category(qs, data):
    if data["category"]:
        category = data["category"]
        if category.parent is None:
            qs = qs.filter(Event.id==PageSet.event_id).filter(PageSet.parent_id==Category.pageset_id).filter(Category.origin==category.origin)
        else:
            qs = qs.filter(Event.id==PageSet.event_id).filter(PageSet.parent_id==Category.pageset_id).filter(Category.id==category.id)
    return qs

