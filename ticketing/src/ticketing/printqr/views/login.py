# -*- coding:utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from ticketing.printqr import forms
from ticketing.printqr.security import login, logout

@view_config(route_name="login", request_method="GET", renderer="ticketing.printqr:templates/login.html")
def login_view(request):
    form = forms.LoginForm()
    return {"form": form}

@view_config(route_name="login", request_method="POST", renderer="ticketing.printqr:templates/login.html")
def login_post_view(request):
    form = forms.LoginForm(request.POST)
    if not form.validate():
        return {"form": form}
    else:
        headers = login(request, form.data["login_id"], form.data["password"])
        return HTTPFound(location=request.route_url("index"), headers=headers)

@view_config(route_name="logout", request_method="POST")
def logout_view(request):
    logout(request)
    request.session.flash(u"ログアウトしました")
    return HTTPFound(location=request.route_url("login"))
