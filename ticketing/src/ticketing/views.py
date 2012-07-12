# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.view import view_config

from ticketing.fanstatic import with_bootstrap
from ticketing.fanstatic import bootstrap_need

from pyramid.url import route_path
class BaseView(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

    def location(self, route_name):
        return HTTPFound(location=route_path(route_name, self.request))

@view_defaults(decorator=with_bootstrap)
class CommonView(BaseView):

    @view_config(route_name='index', renderer='ticketing:templates/index.html')
    def index(self):
        return HTTPFound(location=route_path('events.index', self.request))

    @view_config(context=HTTPForbidden, renderer='ticketing:templates/common/forbidden.html')
    def forbidden_view(self):

        if authenticated_userid(self.request):
            return {}

        loc = self.request.route_url('login.index', _query=(('next', self.request.url),))

        return HTTPFound(location=loc)


