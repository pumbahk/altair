# -*- coding:utf-8 -*-
from altaircms.lib.itertools import find_or_first

def event_page_section_panel(context, request, event):
    pagesets = event.pagesets
    return dict(pagesets=pagesets, 
                page_title=u"配下のページ一覧", 
                current_event=event)

def event_performance_section_panel(context, request, event, id_key="performance_id"):
    performances = event.performances
    if not performances:
        return dict(performances=[], page_title=u"パフォーマンス", current_event=event)
    performance_id = unicode(request.GET.get(id_key))
    if performance_id:
        current_performance = find_or_first(performances, lambda p : unicode(p.id) == performance_id)
    else:
        current_performance = performances[0]
    return dict(current_performance=current_performance, 
                performances=performances, 
                page_title=u"パフォーマンス")

def event_description_section_panel(context, request, event):
    return dict(event=event, page_title=u"文言情報")

