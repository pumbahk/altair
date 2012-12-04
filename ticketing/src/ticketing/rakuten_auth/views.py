# -*- coding:utf-8 -*-
import logging
import pickle

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.view import view_config
from pyramid.response import Response
from pyramid import security

from .api import get_open_id_consumer, authenticated_user, remember_user, get_return_url

logger = logging.getLogger(__name__)

class RootView(object):
    def __init__(self, request):
        self.request = request

    @property
    def consumer(self):
        return get_open_id_consumer(self.request)


    def login(self):
        return HTTPUnauthorized()

    def verify(self):
        return_url = get_return_url(self.request)
        if return_url:
            return HTTPFound(location=return_url)
        else:
            ''' '''
            # return HTTPFound(location="/mypage")

    def error(self):
        return Response(body="auth error")
        
