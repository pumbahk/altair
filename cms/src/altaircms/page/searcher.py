from .helpers import pageset_id_list_from_word
from ..page.models import PageSet
from ..models import Category
from datetime import datetime

def make_pageset_search_query(request, data, qs=None, today=None):
    today = today or datetime.now()
    qs = qs or PageSet.query    
    qs = make_pageset_search_by_word(request, qs, data)
    qs = make_pageset_search_by_category(qs, data)
    if data["is_vetoed"]:
        import warnings
        warnings.warn("not implemented yet")
    return qs

def make_pageset_search_by_word(request, qs, data):
    ## search by solr
    if data["freeword"]:
        word = data["freeword"]
        # pagesets = pageset_id_list_from_word(request, word)
        # qs = qs.filter(PageSet.id.in_(pagesets))
        qs.filter(PageSet.name.like(u"%%%s%%" % word))
    return qs


def make_pageset_search_by_category(qs, data):
    if data["category"]:
        category = data["category"]
        if category.parent is None:
            qs = qs.filter(PageSet.parent_id==Category.pageset_id).filter(Category.origin==category.origin)
        else:
            qs = qs.filter(PageSet.parent_id==Category.pageset_id).filter(Category.id==category.id)
    return qs

