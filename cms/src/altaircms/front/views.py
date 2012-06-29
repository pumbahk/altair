# coding: utf-8

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_config


@view_config(route_name="preview_page")
def preview_page(context, request):
    control = context.access_control()
    access_key = request.params.get("access_key")
    page_id = request.matchdict["page_id"]
    page = control.fetch_page_from_pageid(page_id, access_key=access_key)

    if not control.can_access():
        return HTTPForbidden(control.error_message)
    
    template = context.frontpage_template(page)
    if not control.can_rendering(template, page):
        raise HTTPInternalServerError(control.error_message)

    renderer = context.frontpage_renderer()
    return renderer.render(template, page)


@view_config(route_name="preview_pageset")
def preview_pageset(context, request):
    control = context.access_control()
    pageset_id = request.matchdict["pageset_id"]
    page = control.fetch_page_from_pagesetid(pageset_id)

    if not control.can_access():
        return HTTPForbidden()
    
    template = context.frontpage_template(page)
    if not control.can_rendering(template, page):
        raise HTTPInternalServerError(control.error_message)

    renderer = context.frontpage_renderer()
    return renderer.render(template, page)
