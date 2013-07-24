# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from altair.app.ticketing.core.api import get_organization
from .forms import NowSettingForm
from altair.now import (
    get_now, 
    set_now, 
    has_session_key
)
# from altair.app.ticketing.views import BaseView
@view_config(route_name="whattime.nowsetting.form", permission="cart_admin", renderer="altair.app.ticketing.whattime:templates/nowsetting/form.html")
def form_view(context, request):
    now = get_now(request)
    form = NowSettingForm(now=now, redirect_to=request.GET.get("redirect_to", ""))
    organization = get_organization(request)
    return {"form": form, "now": now, "now_found": has_session_key(request), "organization": organization}

@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="submit")
def now_set_view(context, request):
    form = NowSettingForm(request.POST)
    if not form.validate():
        now = get_now(request)
        organization = get_organization(request)
        return {"form": form, "now": now, "has_key": has_session_key(request), "organization": organization}        
    set_now(request, form.data["now"])
    return HTTPFound(request.route_path("whattime.nowsetting.form", _query=dict(request.GET)))

@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="goto")
def now_gotot_view(context, request):
    return HTTPFound(request.params.get("redirect_to") or request.route_path("whattime.nowsetting.form"))

@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="invalidate")
def now_invalidate_view(context, request):
    set_now(request, None)
    return HTTPFound(request.route_path("whattime.nowsetting.form", _query=dict(request.GET)))
