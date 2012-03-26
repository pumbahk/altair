# -*- coding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid

def add_routes(config):
    config.add_route('index'    , '/')
    config.include('ticketing.views.admin.add_routes' , route_prefix='/admin')
    config.include('ticketing.views.login.add_routes' , route_prefix='/login')
    config.include('ticketing.views.api.add_routes'   , route_prefix='/api')
    config.include('ticketing.views.events.add_routes' , route_prefix='/events')
    config.include('ticketing.views.operators.add_routes' , route_prefix='/operators')

class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.operator = context.user

@view_config(context=HTTPForbidden)
def forbidden_view(request):

    if authenticated_userid(request):
        return render_to_response('ticketing:templates/common/forbidden.html', {},request=request)
    loc = request.route_url('login.index', _query=(('next', request.url),))

    return HTTPFound(location=loc)