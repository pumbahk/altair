# coding: utf-8
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

@view_config(route_name="front")
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    page, layout = context.get_page_and_layout(url)

    block_context = context.get_block_context(page)
    block_context.scan(request=request)

    tmpl = context.get_layout_template(layout, context.get_render_config())
    params = dict(page=page, display_blocks=block_context.blocks)
    return render_to_response(tmpl, params, request)

@view_config(route_name="front_preview")
def rendering_preview_page(context, request):
    url = request.matchdict["page_name"]
    page, layout = context.get_page_and_layout_preview(url)

    block_context = context.get_block_context(page)
    block_context.scan(request=request)

    tmpl = context.get_layout_template(layout, context.get_render_config())
    params = dict(page=page, display_blocks=block_context.blocks)
    return render_to_response(tmpl, params, request)

@view_config(route_name="front_to_preview") #slack-off
def to_preview_page(context, request):
    page_id = request.matchdict["page_id"]
    page = context.get_unpublished_page(page_id)
    return HTTPFound(request.route_url("front_preview", page_name=page.hash_url))

