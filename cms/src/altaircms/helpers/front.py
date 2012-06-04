# -*- coding:utf-8 -*-

## todo:あとでtemplateに利用している関数の名前揃える。
## todo:ここにある関数を全部./link.pyに持っていく
import logging
logger = logging.getLogger(__name__)
from .link import to_publish_page_from_pageset

def to_preview_page(request, page):
    logger.debug('preview')
    return request.route_path("front_preview", page_id=page.id, page_name=page.hash_url)
