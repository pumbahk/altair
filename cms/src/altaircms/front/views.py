# coding: utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from datetime import datetime
from ..helpers.front import to_preview_page
from ..page.models import PageSet

@view_config(route_name="front_preview_pageset")
def redirect_preview_pageset(request):
    pageset = PageSet.query.filter(PageSet.id==request.matchdict["pageset_id"]).one()
    return HTTPFound(to_preview_page(request, pageset.current()))

# @view_config(route_name="front", decorator=with_jquery)
# def rendering_page(context, request):
#     url =  api.usersite_url(request)
#     return HTTPFound(urlparse.urljoin(url, request.matchdict["page_name"]))

# @view_config(route_name="front_preview", decorator=with_jquery)
# def rendering_preview_page(context, request):
#     url =  api.usersite_url(request)
#     return HTTPFound(urlparse.urljoin(url, request.matchdict["page_name"]))
