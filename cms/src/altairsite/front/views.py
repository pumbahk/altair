# coding: utf-8
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from altaircms.lib.fanstatic_decorator import with_jquery
from altaircms.page.api import as_static_page_response, StaticPageNotFound
from ..mobile import api as mobile_api
from altairsite.mobile.custom_predicates import mobile_access_predicate
import logging 
logger = logging.getLogger(__name__)

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

EXCLUDE_EXT_LIST = (".ico", ".js", ".css")
@view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.pc_access_control()

    try:
        static_page = control.fetch_static_page_from_params(url, dt)
        if static_page:
            return as_static_page_response(request, static_page, url)
    except StaticPageNotFound as e:
        logger.info(str(e))

    if request.url.endswith(EXCLUDE_EXT_LIST):
        return HTTPNotFound()

    page = control.fetch_page_from_params(url, dt)

    if not control.can_access():
        raise HTTPNotFound(control.error_message)

    template = control.frontpage_template(page)
    if template is None:
        logger.warn("front pc access template is not found layout=%s template_file=%s" % (page.layout.id, page.layout.template_filename))
        raise HTTPNotFound("template is not found")

    renderer = control.frontpage_renderer()
    response = renderer.render(template, page)
    return response

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
        logging.info(control.error_message)
        raise HTTPNotFound(control.error_message)
