# coding: utf-8

from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config
from altaircms.lib.fanstatic_decorator import with_jquery
from . import api

from altairsite.mobile.custom_predicates import mobile_access_predicate
from altairsite.mobile.response import convert_response_for_mobile

## todo refactoring
"""
ここのviewはwidgetなどの情報を集めて、ページをレンダリングするview。
どのテンプレートを利用するかは実行時に決まる。(render_to_responseを利用)

viewの種類2つ（これは後で綺麗にしたい)

+ publish        ---- 公開されたページのレンダリング(url存在)
+ preview        ---- 非公開のページをハッシュ値つけたURLでレンダリング

"""


"""
todo:
カテゴリトップかイベント詳細ページかで表示方法を分ける必要がある
カテゴリトップの場合には、サブジャンルを取得できる必要がある。
"""

def _rendering(context, request, page, layout):
    block_context = context.get_block_context(page)
    block_context.scan(request=request,
                       page=page, 
                       performances=context.get_performances(page),
                       event=page.event)
    tmpl = context.get_layout_template(layout, context.get_render_config())

    params = api.get_navigation_categories(request)
    params.update(sub_categories=api.get_subcategories_from_page(request, page))
    params.update(page=page, display_blocks=block_context.blocks)
    return render_to_response(tmpl, params, request)


@view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()
    page, layout = context.get_page_and_layout(url, dt)
    return _rendering(context, request, page, layout)

@view_config(route_name="front", custom_predicates=(mobile_access_predicate,))
def rendering_page_mobile(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()
    page, layout = context.get_page_and_layout(url, dt)

    from altaircms.layout.models import Layout
    layout = Layout.query.filter_by(template_filename="m."+layout.template_filename).first() ## too ad-hoc. fix after experimentation.
    return convert_response_for_mobile(_rendering(context, request, page, layout))

@view_config(route_name="front_preview", decorator=with_jquery)
def rendering_preview_page(context, request):
    url = request.matchdict["page_name"]
    page, layout = context.get_page_and_layout_preview(url, request.matchdict["page_id"])
    return _rendering(context, request, page, layout)

@view_config(route_name="front_to_preview") #slack-off
def to_preview_page(context, request):
    import warnings
    warnings.warn("this-is-obsolute function. don't use it.")
    page_id = request.matchdict["page_id"]
    page = context.get_unpublished_page(page_id)
    return HTTPFound(request.route_path("front_preview", page_name=page.hash_url))
