# coding: utf-8

import urlparse
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from altaircms.lib.fanstatic_decorator import with_jquery
from . import api


@view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url =  api.usersite_url(request)
    return HTTPFound(urlparse.urljoin(url, request.matchdict["page_name"]))

@view_config(route_name="front_preview", decorator=with_jquery)
def rendering_preview_page(context, request):
    url =  api.usersite_url(request)
    return HTTPFound(urlparse.urljoin(url, request.matchdict["page_name"]))
