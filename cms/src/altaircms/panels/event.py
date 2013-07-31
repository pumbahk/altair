# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from altaircms.lib.itertools import find_or_first
from altaircms.auth.accesskey.api import get_event_access_key_control
from altaircms.auth.models import PageAccesskey
from altaircms.linklib import get_cart_url_builder
from functools import partial

def event_page_section_panel(context, request, event):
    pagesets = event.pagesets
    return dict(pagesets=pagesets, 
                page_title=u"配下のページ一覧", 
                current_event=event)

def event_performance_section_panel(context, request, event, id_key="performance_id"):
    performances = event.performances
    if not performances:
        return dict(performances=[], page_title=u"パフォーマンス", event=event)
    performance_id = unicode(request.GET.get(id_key))
    if performance_id:
        current_performance = find_or_first(performances, lambda p : unicode(p.id) == performance_id)
    else:
        current_performance = performances[0]
    return dict(current_performance=current_performance, 
                event=event, 
                performances=performances, 
                page_title=u"パフォーマンス")

def event_description_section_panel(context, request, event):
    return dict(event=event, page_title=u"文言情報")

def event_accesskey_section_panel(context, request, event):
    control = get_event_access_key_control(request, event)
    accesskeys = control.query_access_key().options(orm.joinedload(PageAccesskey.operator)).all()

    whattime_url_gen = partial(get_cart_url_builder(request).whattime_form_url, event)
    def generate_url(hashkey):
        return whattime_url_gen(_query=dict(accesskey=hashkey, event_id=event.id))
    return dict(event=event, page_title=u"アクセスキー", 
                preview_with_accesskey_url_gen=generate_url , 
                create_accesskey_url=request.route_path("auth.accesskey.eventkey",action="create", event_id=event.id), 
                update_accesskey_url=request.route_path("auth.accesskey.detail", accesskey_id="__id__", _query=dict(endpoint=request.url)), 
                delete_accesskey_url=request.route_path("auth.accesskey.eventkey",action="delete", event_id=event.id), 
                accesskeys=accesskeys)
