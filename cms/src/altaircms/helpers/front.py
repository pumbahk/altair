# -*- coding:utf-8 -*-

## todo:あとでtemplateに利用している関数の名前揃える。

def to_preview_page(request, page):
    if page.is_published():
        return _to_publish_page(request, page)
    else:
        return _to_preview_page(request, page)
to_publish_page = to_preview_page

def _to_preview_page(request, page):
    return request.route_path("front_preview", page_name=page.hash_url)

def _to_publish_page(request, page):
    return request.route_path("front", page_name=page.url)

