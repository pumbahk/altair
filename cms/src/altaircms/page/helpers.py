## for viewlet
from pyramid.view import render_view_to_response
from markupsafe import Markup
from ..viewlet import api as va

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
