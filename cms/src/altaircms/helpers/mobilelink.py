# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)

import warnings
def get_purchase_page_from_event(request, event):
    warnings.warn("this is ad-hoc definition please fixme!")

    if event.backend_id is None:
        logger.warn("event id=%d: evnt backend_id is not found" % event.id)
    return u"/m/cart/events/%s" % event.backend_id

def get_purchase_page_from_performance(request, performance):
    warnings.warn("this is ad-hoc definition please fixme!")

    if performance.purchase_link:
        return performance.purchase_link

    if performance.backend_id is None:
        logger.warn("event id=%d performance id=%d: performancr backend_id is not found" % (performance.event.id, performance.id))
    return u"/cart/events/%s?performance=%s" % (performance.event.backend_id, performance.backend_id)


def get_searchpage(request, kind=None, value=None):
    warnings.warn("this is ad-hoc definition please fixme!")
    return request.route_path("page_search_by", kind=kind, value=value)

def get_link_from_category(request, category):
    return to_publish_page_from_pageset(request, category.pageset)

def get_link_from_topic(request, topic):
    if topic.mobile_link:
        return topic.mobile_link
    elif topic.linked_page:
        return to_publish_page_from_pageset(request, topic.linked_page)
    else:
        return ""

get_link_from_topcontent = get_link_from_topic

def unquote_path_segment(string):
    """ request.route_pathの結果"foo/bar"が "foo%2Fbar"になってしまう部分の修正。
    (request_route_pathは、pyramid.traversal.qoute_path_segmentを実行された結果を利用する)
    """
    return string.replace("%2F", "/") #buggy!

def to_publish_page_from_pageset(request, pageset):
    ## mobile用pageはversion管理されていない
    return request.route_path("mobile_detail", pageset_id=pageset.id)

def to_preview_page_from_pageset(request, pageset):
    warnings.warn("this is ad-hoc definition please fixme!")
    url = pageset.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return unquote_path_segment(request.route_path("front_preview_pageset", pageset_id=pageset.id))
