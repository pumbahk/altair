# -*- coding:utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from altair.app.ticketing.core.api import get_organization
from altair.preview.api import (
    set_after_invalidate_url, 
    set_force_request_type
)
from .forms import NowSettingForm
from .description import description_iterate
from .external import CandidatesURLDictBuilder
from altair.now import (
    get_now, 
    set_now, 
    has_session_key
)

from .api import get_cms_accesskey
# from ticketing.views import BaseView

import logging
logger = logging.getLogger(__name__)

def has_cms_login_key(info, request):
    if "salt" in request.session and request.GET.get("accesskey") == request.session.get("salt", object()): #hmm
        return True
    k = request.GET.get("accesskey")
    if not k:
        logger.info("not accesskey")
        return False
    accesskey = get_cms_accesskey(request, k)
    if not accesskey:
        logger.info("not access key response")
        return False
    request.accesskey = accesskey
    return True

@view_config(route_name="whattime.nowsetting.form", custom_predicates=(has_cms_login_key, ),
             renderer="altair.app.ticketing.whattime:templates/nowsetting/form.html")
@view_config(route_name="whattime.nowsetting.form", permission="cart_admin",
             renderer="altair.app.ticketing.whattime:templates/nowsetting/form.html")
def form_view(context, request):
    now = get_now(request)
    form = NowSettingForm(now=now, redirect_to=request.GET.get("redirect_to", ""))
    organization = get_organization(request)
    candidates_url_dict = CandidatesURLDictBuilder(request).build(request.GET.get("event_id"), request.GET.get("backend_event_id"))
    return {"form": form, "now": now, "now_found": has_session_key(request), "organization": organization, 
            "description_itr": description_iterate(request), "candidates_url_dict": candidates_url_dict}

def _treat_dict(request, d2):
    D = request.GET.copy()
    D.update(d2)
    for k in ["invalidate", "submit", "goto", "request_type"]:
        if k in D:
            D.pop(k)
    return D

@view_config(route_name="whattime.nowsetting.set",custom_predicates=(has_cms_login_key, ), request_method="POST", request_param="submit", 
             renderer="altair.app.ticketing.whattime:templates/nowsetting/form.html")
@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="submit", 
             renderer="altair.app.ticketing.whattime:templates/nowsetting/form.html")
def now_set_view(context, request):
    form = NowSettingForm(request.POST)
    if not form.validate():
        now = get_now(request)
        organization = get_organization(request)
        candidates_url_dict = CandidatesURLDictBuilder(request).build(request.GET.get("event_id"), request.GET.get("backend_event_id"))
        return {"form": form, "now": now, "has_key": has_session_key(request), "organization": organization, 
                "description_itr": description_iterate(request), "candidates_url_dict": candidates_url_dict}
 
    set_now(request, form.data["now"])
    request.session.flash(u"現在時刻が「{now}」に設定されました".format(now=form.data["now"]))
    return HTTPFound(request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, form.data)))


@view_config(route_name="whattime.nowsetting.set", custom_predicates=(has_cms_login_key, ), request_method="POST", request_param="goto")
@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="goto")
def now_goto_view(context, request):
    set_after_invalidate_url(request, request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, request.GET)))
    if not has_session_key(request):
        request.session.flash(u"現在時刻が設定されていません")
        raise HTTPFound(request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, request.GET)))
    return HTTPFound(request.params.get("redirect_to") or request.route_path("whattime.nowsetting.form"))

@view_config(route_name="whattime.nowsetting.set", custom_predicates=(has_cms_login_key, ), request_method="POST", request_param="invalidate")
@view_config(route_name="whattime.nowsetting.set", permission="cart_admin", request_method="POST", request_param="invalidate")
def now_invalidate_view(context, request):
    set_now(request, None)
    request.session.flash(u"現在時刻の設定が取り消されました")
    return HTTPFound(request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, request.POST)))

@view_config(route_name="whattime.nowsetting.goto", custom_predicates=(has_cms_login_key, ), request_param="redirect_to")
@view_config(route_name="whattime.nowsetting.goto", permission="cart_admin", request_param="redirect_to")
def now_goto_redirect_view(context, request):
    if "request_type" in request.GET:
        try:
            set_force_request_type(request, request.GET["request_type"])
        except ValueError:
            raise HTTPBadRequest("invalid request type")
    if not has_session_key(request):
        request.session.flash(u"現在時刻が設定されていません")
        raise HTTPFound(request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, request.GET)))
    set_after_invalidate_url(request, request.route_path("whattime.nowsetting.form", _query=_treat_dict(request, request.GET)))
    return HTTPFound(request.GET.get("redirect_to"))
