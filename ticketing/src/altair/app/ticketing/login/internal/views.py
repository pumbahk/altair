# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPFound
import logging
logger = logging.getLogger(__name__)
from .forms import LoginForm
from . import security

def login_view(context, request):
    logger.debug("login")
    form = LoginForm()
    return {"form": form}

def login_post_view(context, request):
    form = LoginForm(request.POST)
    if  context.login_validate(form):
        headers = security.login(request, form.data["login_id"], form.data["password"])
        return HTTPFound(location=context.get_after_login_url( _query=request.GET), headers=headers)
    else:
        return {"form": form}

def logout_view(context, request):
    headers = security.logout(request)
    request.session.flash(u"ログアウトしました")
    return HTTPFound(location=request.route_path("login"), headers=headers)
