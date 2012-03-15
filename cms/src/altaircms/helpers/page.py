# -*- coding:utf-8 -*-

def show_publish_status(page):
    if page.is_published():
        return u"公開中"
    else:
        return u"プライベート"

def to_edit_page(request, page):
    if page.event is None:
        return request.route_path("page_edit_", page_id=page.id)
    else:
        return request.route_path("page_edit", event_id=page.event.id, page_id=page.id)

def to_list_page(request):
    return request.route_path("page")

def to_delete(request, page):
    return request.route_path("page_delete", id=page.id)

def to_update(request, page):
    return request.route_path("page_update", id=page.id)
