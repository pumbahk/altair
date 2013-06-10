# coding: utf-8
from pyramid.httpexceptions import HTTPNotFound
from altaircms.lib.fanstatic_decorator import with_jquery
from altaircms.page.staticupload.api import as_static_page_response, StaticPageNotFound
import logging 
import os.path
from altairsite.config import usersite_view_config
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

def _rendering_page(context, request, control, page): #todo: refactoring
    descriptor = control.frontpage_discriptor(page)
    if not descriptor.exists():
        logger.info("front pc access template is not found layout=%s template_file=%s" % (page.layout.id, descriptor.absspec()))
        raise HTTPNotFound("template is not found")

    renderer = control.frontpage_renderer()
    response = renderer.render(descriptor.absspec(), page)
    return response
    
EXCLUDE_EXT_LIST = (".ico", ".js", ".css")
@usersite_view_config(route_name="front", decorator=with_jquery)
def rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.pc_access_control()

    try:
        static_page = control.fetch_static_page_from_params(url, dt)
        if static_page:
            return as_static_page_response(request, static_page, url)
    except StaticPageNotFound:
        logger.info(u'no corresponding static page found for url=%s; falls back to standard page discovery' % url)

    if os.path.splitext(request.url)[1] != "":
        return HTTPNotFound()

    page = control.fetch_page_from_params(url, dt)

    if not control.can_access():
        logger.info(control.error_message)
        raise HTTPNotFound(control.error_message)
    return _rendering_page(context, request, control, page)

from altairsite.mobile.dispatch.views import dispatch_view as mobile_dispatch_view
from altairsite.smartphone.dispatch.views import dispatch_view as smartphone_dispatch_view
from pyramid.httpexceptions import HTTPFound

@usersite_view_config(route_name="front", request_type="altairsite.tweens.IMobileRequest")
def mobile_rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.pc_access_control()
    page = control.fetch_page_from_params(url, dt)

    if not control.access_ok or page.event_id is None:
        logger.info(control.error_message)
        return mobile_dispatch_view(context, request)
    return HTTPFound(request.route_path("eventdetail", _query=dict(event_id=page.event_id or page.pageset.event_id)))
    
@usersite_view_config(route_name="front", request_type="altairsite.tweens.ISmartphoneRequest")
def smartphone_rendering_page(context, request):
    url = request.matchdict["page_name"]
    dt = context.get_preview_date()

    control = context.pc_access_control()
    page = control.fetch_page_from_params(url, dt)

    if not control.access_ok:
        logger.info(control.error_message)
        return smartphone_dispatch_view(context, request)
    if page.event_id is None:
        ## TOOOOOOOOOOOOO adhoc.
        if page.url.startswith("special"):
            return _rendering_page(context, request, control, page)
        else:
            return smartphone_dispatch_view(context, request)
    return HTTPFound(request.route_path("smartphone.detail", _query=dict(event_id=page.event_id or page.pageset.event_id)))
    
