# -*- coding:utf-8 -*-
from altairsite.config import smartphone_site_view_config
from altair.mobile.api import set_we_need_pc_access
from altair.mobile.api import set_we_invalidate_pc_access
from pyramid.httpexceptions import HTTPFound
from .common.helper import SmartPhoneHelper
import random

### main_pc view is bound by config.add_view (__init__.py)

def main(context, request):
    return context.get_top_render_param()

def main_pc(context, request):
    ## don't imitate. this.
    return {'helper':SmartPhoneHelper()}

@smartphone_site_view_config(route_name="smartphone.goto_pc_page", request_type="altair.mobile.interfaces.ISmartphoneRequest")
def goto_pc_page(context, request):
    response = HTTPFound(request.GET.get("next", "/"))
    set_we_need_pc_access(response)
    return response

@smartphone_site_view_config(route_name="smartphone.goto_sp_page")
def goto_sp_page(context, request):
    response = HTTPFound(request.GET.get("next", request.route_path("smartphone.main"))) #todo: change
    set_we_invalidate_pc_access(response)
    return response
