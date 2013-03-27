# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.url import route_path

class BaseView(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

    def location(self, route_name):
        return HTTPFound(location=route_path(route_name, self.request))
