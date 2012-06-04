# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated, authenticated_userid

from newsletter.fanstatic import with_bootstrap

class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

@view_defaults(decorator=with_bootstrap)
class CommonView(BaseView):

    @view_config(route_name='index', renderer='newsletter:templates/index.html')
    def index(self):
        return {}

    @view_config(context=HTTPForbidden, renderer='newsletter:templates/common/forbidden.html')
    def forbidden_view(self):
        if authenticated_userid(self.request):
            return {}

        loc = self.request.route_url('login.index', _query=(('next', self.request.url),))

        return HTTPFound(location=loc)
