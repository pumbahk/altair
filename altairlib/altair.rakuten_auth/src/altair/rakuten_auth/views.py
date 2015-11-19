# -*- coding:utf-8 -*-
import logging
from pyramid import security
from .interfaces import IRakutenOpenID
from pyramid.httpexceptions import HTTPUnauthorized, HTTPInternalServerError 

logger = logging.getLogger(__name__)

class RootView(object):
    def __init__(self, request):
        self.request = request

    def _get_impl(self):
        return self.request.registry.queryUtility(IRakutenOpenID)

    def login(self):
        return HTTPUnauthorized()

    def verify(self):
        impl = self._get_impl()
        return impl.on_verify(self.request)

    def verify2(self):
        impl = self._get_impl()
        return impl.on_extra_verify(self.request)

    def error(self):
        return HTTPInternalServerError(body="auth error")
