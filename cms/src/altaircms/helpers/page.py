# -*- coding:utf-8 -*-

def show_publish_status(page):
    if page.is_published():
        return u"公開中"
    else:
        return u"プライベート"

def to_edit_page(request, page):
    if page.event is None:
        return request.route_url("page_edit_", page_id=page.id)
    else:
        return request.route_url("page_edit", event_id=page.event.id, page_id=page.id)

def to_list_page(request):
    return request.route_url("page")

def to_delete(request, page):
    return request.route_url("page_delete", id=page.id)

def to_update(request, page):
    return request.route_url("page_update", id=page.id)

def to_update_confirm(request, page):
    return request.route_url("page_update_confirm", id=page.id)

## todo:rename
def to_settings(request, page):
    return request.route_url("page_settings", id=page.id)

# def to_update(request, page):
#     return request.route_url("page_update", id=page.id)
