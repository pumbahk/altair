# -*- coding: utf-8 -*-

from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated
from pyramid.security import authenticated_userid
from pyramid.url import route_path

from ticketing.fanstatic import with_bootstrap
from ticketing.interfaces import IAPIContext
from ticketing.cart.interfaces import IMobileRequest

class Predicate(object):
    def __invert__(self):
        return lambda *args, **kwargs: not self(*args, **kwargs)

    def __mul__(self, that):
        return lambda *args, **kwargs: self(*args, **kwargs) and that(*args, **kwargs)

    def __add__(self, that):
        return lambda *args, **kwargs: self(*args, **kwargs) or that(*args, **kwargs)

class MobileRequestPredicate(Predicate):
    def __call__(self, request):
        return IMobileRequest.providedBy(request) 

mobile_request = MobileRequestPredicate()

class BaseView(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

    def location(self, route_name):
        return HTTPFound(location=route_path(route_name, self.request))
