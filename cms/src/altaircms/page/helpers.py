## for viewlet
from pyramid.view import render_view_to_response
from markupsafe import Markup
from ..viewlet import api as va
from ..tag.models import HotWord ## ugly
from ..solr.api import pageset_id_list_from_word
from pyramid.interfaces import IRootFactory
from ..tag.api import get_tagmanager
from ..asset.api import set_taglabel
from ..topic.models import Topic
from ..topic.models import Topcontent

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

def event_pageset_describe_viewlet(request, pageset):
    va.set_event(request, pageset.event)
    va.set_pagesets(request, [pageset])
    context = request.registry.getUtility(IRootFactory)(request)
    response = render_view_to_response(context, request, name="describe_pageset")
    if response is None:
        raise ValueError
    return Markup(response.text)

def asset_describe_viewlet(request, pageset):
    tmanager = get_tagmanager("asset", request) ##
    assets = tmanager.search_by_tag_label(pageset.taglabel)
    va.set_assets(request, assets)
    set_taglabel(request, pageset.taglabel)
    response = render_view_to_response(request.context, request, name="describe_asset")
    if response is None:
        raise ValueError
    return Markup(response.text)


def topic_describe_viewlet(request, pageset):
    va.set_pageset(request, pageset)
    event = pageset.event
    va.set_event(request, event)
    topics = Topic.query.filter_by(event=event).filter_by(bound_page=pageset).order_by("topic.kind", "topic.subkind", "topic.display_order")
    va.set_topics(request, topics)
    response = render_view_to_response(request.context, request, name="describe_topic")
    if response is None:
        raise ValueError
    return Markup(response.text)

def topcontent_describe_viewlet(request, pageset):
    va.set_pageset(request, pageset)
    topcontents = Topcontent.query.filter_by(bound_page=pageset).order_by("topcontent.kind", "topcontent.subkind", "topcontent.display_order")
    va.set_topcontents(request, topcontents)
    response = render_view_to_response(request.context, request, name="describe_topcontent")
    if response is None:
        raise ValueError
    return Markup(response.text)
