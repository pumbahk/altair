# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPFound,HTTPBadRequest
import logging
logger = logging.getLogger(__name__)
from .forms import LoginForm
from . import security
from webob.multidict import MultiDict

def login_view(context, request):
    logger.debug("login")
    form = LoginForm()
    return {"form": form}

def login_post_view(context, request):
    form = LoginForm(request.POST)
    if  context.login_validate(form):
        headers = security.login(request, form.data["login_id"], form.data["password"])
        logger.info("*login login sucess name=%s", form.data["login_id"])
        return HTTPFound(location=context.get_after_login_url( _query=request.GET), headers=headers)
    else:
        return {"form": form}

def logout_view(context, request):
    operator = context.operator
    if operator is None:
        request.session.flash(u"既にログアウトしているようです")
        raise HTTPFound(location=request.route_path("login"))
    headers = security.logout(request)
    request.session.flash(u"ログアウトしました")
    logger.info("*login logout name=%s", operator.name)
    return HTTPFound(location=request.route_path("login"), headers=headers)

## api
def login_post_api_view(context, request):
    form = LoginForm(MultiDict(request.json_body))
    if context.login_validate(form):
        headers = security.login(request, form.data["login_id"], form.data["password"])
        logger.info("*login login success name=%s", form.data["login_id"])
        request.response.headers = headers
        return context.on_after_login(form.operator)
    else:
        if form.data.has_key("login_id"):
            logger.info("*login login failure name=%s", form.data["login_id"])
        if form.errors.has_key("login_id"):
            return HTTPBadRequest(u"E@:{}".format(form.errors["login_id"][0])) #xxx:
        else:
            return HTTPBadRequest(u"E@ login failure!")

def logout_api_view(context, request):
    operator = context.operator
    headers = security.logout(request)
    logger.info("*login logout name=%s", operator.name)
    request.response.headers = headers
    return context.on_after_logout(operator)
