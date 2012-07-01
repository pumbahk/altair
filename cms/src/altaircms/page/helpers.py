## for viewlet
from pyramid.view import render_view_to_response
from markupsafe import Markup
from ..viewlet import api as va
from altaircms.tag.models import HotWord ## ugly

def _extract_tags(params, k):
    if k not in params:
        return []
    tags = [e.strip() for e in params.pop(k).split(",")] ##
    return [k for k in tags if k]

def divide_data(params):
    tags = _extract_tags(params, "tags")
    private_tags = _extract_tags(params, "private_tags")
    return tags, private_tags, params

def pagetag_describe_viewlet(request, page):
    va.set_page(request, page)
    va.set_tags(request, page.tags)
    response = render_view_to_response(request.context, request, name="describe_pagetag")
    if response is None:
        raise ValueError
    return Markup(response.text)

def hotword_describe_viewlet(request, page):
    va.set_page(request, page)
    hotwords = HotWord.from_page(page)
    va.set_hotwords(request, hotwords)
    response = render_view_to_response(request.context, request, name="describe_hotword")
    if response is None:
        raise ValueError
    return Markup(response.text)

def accesskey_describe_viewlet(request, page):
    va.set_page(request, page)
    accesskeys = page.access_keys
    va.set_accesskeys(request, accesskeys)
    response = render_view_to_response(request.context, request, name="describe_accesskey")
    if response is None:
        raise ValueError
    return Markup(response.text)

def pageset_describe_viewlet(request, pageset):
    va.set_event(request, None)
    va.set_pagesets(request, [pageset])
    response = render_view_to_response(request.context, request, name="describe_pageset")
    if response is None:
        raise ValueError
    return Markup(response.text)

from ..tag.api import get_tagmanager

def asset_describe_viewlet(request, pageset):
    tmanager = get_tagmanager("asset", request) ##
    assets = tmanager.search_by_tag_label(pageset.taglabel)
    va.set_assets(request, assets)

    response = render_view_to_response(request.context, request, name="describe_asset")
    if response is None:
        raise ValueError
    return Markup(response.text)

# def asset_describe_viewlet(request, page):
#     va.set_page(request, page)
#     assets = Asset.from_page(page)
#     va.set_assets(request, assets)
#     response = render_view_to_response(request.context, request, name="describe_asset")
#     if response is None:
#         raise ValueError
#     return Markup(response.text)

# def topic_describe_viewlet(request, page):
#     va.set_page(request, page)
#     topics = Topic.from_page(page)
#     va.set_topics(request, topics)
#     response = render_view_to_response(request.context, request, name="describe_topic")
#     if response is None:
#         raise ValueError
#     return Markup(response.text)

# def topcontent_describe_viewlet(request, page):
#     va.set_page(request, page)
#     topcontents = Topcontent.from_page(page)
#     va.set_topcontents(request, topcontents)
#     response = render_view_to_response(request.context, request, name="describe_topcontent")
#     if response is None:
#         raise ValueError
#     return Markup(response.text)
