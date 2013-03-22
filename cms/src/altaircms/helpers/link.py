# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__file__)
from markupsafe import Markup
from altaircms.interfaces import ICMSRequest

def get_purchase_page_from_event(request, event):
    if event.backend_id is None:
        logger.warn("event id=%d: evnt backend_id is not found" % event.id)
    return u"/cart/events/%s" % event.backend_id

def get_purchase_page_from_performance(request, performance):
    if hasattr(request, "is_mobile") and request.is_mobile:
        if performance.mobile_purchase_link:
            return performance.mobile_purchase_link
    else:
        if performance.purchase_link:
            return performance.purchase_link

    if performance.backend_id is None:
        logger.warn("event id=%d performance id=%d: performancr backend_id is not found" % (performance.event.id, performance.id))
    return u"/cart/events/%s?performance=%s" % (performance.event.backend_id, performance.backend_id)


def get_searchpage(request, kind=None, value=None):
    return request.route_path("page_search_by", kind=kind, value=value)

def get_link_from_category(request, category):
    if category.pageset is None:
        return category.url
    else:
        return publish_page_from_pageset(request, category.pageset)

def get_link_from_genre(request, genre):
    return publish_page_from_pageset(request, genre.category_top_pageset)

def get_link_from_topic_in_cms(request, topic):
    if topic.link:
        return topic.link
    elif topic.linked_page:
        return detail_page_from_pageset(request, topic.linked_page)
    else:
        return ""

get_link_from_topcontent_in_cms = get_link_from_topic_in_cms
get_link_from_promotion_in_cms = get_link_from_topic_in_cms

def get_link_from_topic(request, topic):
    if topic.link:
        return topic.link
    elif topic.linked_page:
        return publish_page_from_pageset(request, topic.linked_page)
    else:
        return ""

get_link_from_topcontent = get_link_from_topic
get_link_from_promotion = get_link_from_topic


def get_link_tag_from_category(request, category):
    return _as_banner_link(request, category) if category.imgsrc else _as_link(request, category)

def _as_banner_link(request, category):
    href = get_link_from_category(request, category)
    return Markup(u'<a href="%s" %s><img src="%s" alt="%s"/></a>' % (href, category.attributes, category.imgsrc, category.label))

def _as_link(request, category):
    href = get_link_from_category(request, category)
    return Markup(u'<a href="%s" %s>%s</a>' % (href, category.attributes, category.label))


def unquote_path_segment(string):
    """ request.route_pathの結果"foo/bar"が "foo%2Fbar"になってしまう部分の修正。
    (request_route_pathは、pyramid.traversal.qoute_path_segmentを実行された結果を利用する)
    """
    return string.replace("%2F", "/") #buggy!

def publish_page_from_pageset(request, pageset):
    url = pageset.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    elif ICMSRequest.providedBy(request):
        return preview_page_from_pageset(request, pageset)
    else:
        return unquote_path_segment(request.route_path("front", page_name=url))

def preview_page_from_pageset(request, pageset):
    url = pageset.url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    else:
        return unquote_path_segment(request.route_path("preview_pageset", pageset_id=pageset.id))

def preview_page_from_page(request, page):
    logger.debug('preview')
    return request.route_path("preview_page", page_id=page.id)

def detail_page_from_pageset(request, pageset):
    if pageset.event_id is None:
        return request.route_path("pageset_detail", pageset_id=pageset.id, kind="other")
    else:
        return request.route_path("pageset_detail", pageset_id=pageset.id, kind="event")
pageset_detail = detail_page_from_pageset
