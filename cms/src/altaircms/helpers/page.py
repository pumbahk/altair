# -*- coding:utf-8 -*-

def show_publish_status(page):
    return u"公開中" if page.published else u"非公開"


def to_edit_page(request, page):
    if page.event is None:
        return request.route_path("page_edit_", page_id=page.id)
    else:
        return request.route_path("page_edit", event_id=page.event.id, page_id=page.id)

def to_update(request, page):
    return request.route_path("page_update", id=page.id)

def event_page(request, page):
    if page.event:
        return request.route_path("event", id=page.event.id)
    else:
        return ""

def get_short_url(keyword):
    return "r-t.jp/" + keyword;

def get_short_url_link(keyword):
    return "https://tools.ticketstar.jp/urlshortener/search?query=" + keyword

