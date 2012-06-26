# coding: utf-8

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from altaircms.lib.fanstatic_decorator import with_jquery
from ..mobile import api as mobile_api
from altairsite.mobile.custom_predicates import mobile_access_predicate

## todo refactoring
"""
ここのviewはwidgetなどの情報を集めて、ページをレンダリングするview。
どのテンプレートを利用するかは実行時に決まる。(render_to_responseを利用)
"""

"""
todo:
カテゴリトップかイベント詳細ページかで表示方法を分ける必要がある
カテゴリトップの場合には、サブジャンルを取得できる必要がある。
"""
@view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.pc_access_control()
    page = control.fetch_page_from_params(url, dt)

    if control.can_access():
        renderer = context.frontpage_renderer()
        return renderer.render(page)
    else:
        return HTTPNotFound(control.error_message)

## for mobile

@view_config(route_name="front", custom_predicates=(mobile_access_predicate,))
def dispatch_view(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.mobile_access_control()
    pageset = control.fetch_pageset_from_params(url, dt)

    if control.can_access():
        raise mobile_api.dispatch_context(request, pageset)
    else:
        return HTTPNotFound(control.error_message)
