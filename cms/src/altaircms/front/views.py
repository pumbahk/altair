# coding: utf-8

from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config


@view_config(route_name="rendering_page")
def rendering_page(context, request):
    control = context.access_controll_from_page(request)
    if not control.can_access():
        return HTTPForbidden()
    return control.rendering_page()


@view_config(route_name="rendering_pageset")
def rendering_pageset(context, request):
    control = context.access_controll_from_pageset(request)
    if not control.can_access():
        return HTTPForbidden()
    return control.rendering_page()

