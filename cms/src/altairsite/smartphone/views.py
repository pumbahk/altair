# -*- coding:utf-8 -*-
from altairsite.config import usersite_view_config
from altairsite.api import set_we_need_pc_access
from altairsite.api import set_we_invalidate_pc_access
from pyramid.httpexceptions import HTTPFound
from altairsite import PC_ACCESS_COOKIE_NAME

@usersite_view_config(route_name='main',request_type="altairsite.tweens.ISmartphoneRequest"
             , renderer='altairsite.smartphone:templates/top.html')
def main(context, request):
    return context.get_top_render_param()

@usersite_view_config(route_name='main',renderer="altairsite.smartphone:templates/pcsite.mock.html")
def main_pc(context, request):
    ## don't imitate. this.
    return {"cookie_name": PC_ACCESS_COOKIE_NAME}

@usersite_view_config(route_name="smartphone.goto_pc_page", request_type="altairsite.tweens.ISmartphoneRequest")
def goto_pc_page(context, request):
    response = HTTPFound(request.GET.get("next", "/")) #todo: change
    set_we_need_pc_access(response)
    return response

@usersite_view_config(route_name="smartphone.goto_sp_page")
def goto_sp_page(context, request):
    response = HTTPFound(request.GET.get("next", "/")) #todo: change
    set_we_invalidate_pc_access(response)
    return response
