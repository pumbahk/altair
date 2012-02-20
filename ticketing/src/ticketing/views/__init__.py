# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid

def add_routes(config):
    config.include('ticketing.views.admin.add_routes' , route_prefix='/admin')
    config.include('ticketing.views.login.add_routes' , route_prefix='/login')

@view_config(context=HTTPForbidden)
def forbidden_view(request):
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login.index', _query=(('next', request.path),('app_id', 'backend'),))
    return HTTPFound(location=loc)