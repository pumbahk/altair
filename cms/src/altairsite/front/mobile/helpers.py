# -*- coding:utf-8 -*-
CATEGORY_SYNONYM = {
    "music": "LiveMusic", 
    "sports": "Sports", 
    "event": "Events", 
    "stage": "performanceArt"
}

from altaircms.models import Category
from altaircms.page.models import PageSet

def get_children_category_from_root(root):
    if root is None:
        ## this is adhoc code. ugly.
        return Category.query.filter_by(parent=None, hierarchy=u"大").filter(Category.name!="index")
    else:
        return Category.query.filter_by(parent=root)

def pageset_query_filter_by_root(qs, root):
    qs = qs.filter(PageSet.event != None)
    if root:
        qs.filter(PageSet.id==Category.pageset_id).filter(Category.origin==root.origin)
    return qs


