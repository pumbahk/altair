# -*- coding:utf-8 -*-

## todo:あとでtemplateに利用している関数の名前揃える。
import logging
logger = logging.getLogger(__name__)

def to_publish_page_from_pageset(request, pageset):
    return request.route_path("front", page_name=pageset.url)

def to_preview_page(request, page):
    logger.debug('to preview page')
    if page.is_published():
        return _to_publish_page(request, page)
    else:
        return _to_preview_page(request, page)

def _to_preview_page(request, page):
    logger.debug('preview')
    query = dict()
    if page.publish_begin:
        query['datetime'] = page.publish_begin.strftime('%Y%m%d%H%M%S')
    return request.route_path("front_preview", page_name=page.hash_url, query=query)

def _to_publish_page(request, page):
    logger.debug('publish')
    query = dict()
    if page.publish_begin:
        query['datetime'] = page.publish_begin.strftime('%Y%m%d%H%M%S')
    return request.route_path("front", page_name=page.url, _query=query)


