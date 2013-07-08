# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPFound
import logging
logger = logging.getLogger(__name__)
from .forms import LoginForm
from . import security

def login_view(request):
    logger.debug("login")
    form = LoginForm()
    return {"form": form}

def login_post_view(request):
    form = LoginForm(request.POST)
    if not form.validate():
        return {"form": form}
    else:
        headers = security.login(request, form.data["login_id"], form.data["password"])
        return HTTPFound(location=request.route_url("eventlist"), headers=headers)

def logout_view(request):
    headers = security.logout(request)
    request.session.flash(u"ログアウトしました")
    return HTTPFound(location=request.route_path("login"), headers=headers)
