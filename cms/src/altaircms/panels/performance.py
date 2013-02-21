# -*- coding:utf-8 -*-
# see. __init__.py
from altaircms.lib.itertools import find_or_first

def performance_describe_panel(context, request, performance):
    salessegments = performance.salessegments
    return dict(performance=performance, 
                sales_segments=salessegments)

def performance_salessegment_tabs_panel(context, request, performance, id_key="salessegment_id"):
    salessegments = performance.salessegments
    salessegment_id = unicode(request.GET.get(id_key))
    if salessegment_id:
        current_salessegment = find_or_first(salessegments, lambda s : unicode(s.id) == salessegment_id)
    else:
        current_salessegment = salessegments[0]
    return dict(current_salessegment=current_salessegment, 
                performance=performance, 
                salessegments=salessegments, 
                page_title=u"販売区分")

