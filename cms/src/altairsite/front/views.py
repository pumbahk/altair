# coding: utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from altaircms.lib.fanstatic_decorator import with_jquery

## todo refactoring
"""
ここのviewはwidgetなどの情報を集めて、ページをレンダリングするview。
どのテンプレートを利用するかは実行時に決まる。(render_to_responseを利用)

viewの種類2つ（これは後で綺麗にしたい)

+ publish        ---- 公開されたページのレンダリング(url存在)
+ preview        ---- 非公開のページをハッシュ値つけたURLでレンダリング

"""

@view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()
    page, layout = context.get_page_and_layout(url, dt)

    block_context = context.get_block_context(page)
    block_context.scan(request=request,
                       page=page, 
                       performances=context.get_performances(page),
                       tickets=context.get_tickets(page), 
                       event=page.event)
    tmpl = context.get_layout_template(layout, context.get_render_config())
    categories = context.get_categories()
    params = dict(page=page, display_blocks=block_context.blocks, categories=categories)
    return render_to_response(tmpl, params, request)

@view_config(route_name="front_preview", decorator=with_jquery)
def rendering_preview_page(context, request):
    url = request.matchdict["page_name"]
    page, layout = context.get_page_and_layout_preview(url)

    block_context = context.get_block_context(page)
    block_context.scan(request=request,
                       page=page, 
                       performances=context.get_performances(page),
                       tickets=context.get_tickets(page), 
                       event=page.event)
    tmpl = context.get_layout_template(layout, context.get_render_config())
    categories = context.get_categories()
    params = dict(page=page, display_blocks=block_context.blocks, categories=categories)
    return render_to_response(tmpl, params, request)

@view_config(route_name="front_to_preview") #slack-off
def to_preview_page(context, request):
    page_id = request.matchdict["page_id"]
    page = context.get_unpublished_page(page_id)
    return HTTPFound(request.route_path("front_preview", page_name=page.hash_url))

