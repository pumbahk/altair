# -*- coding:utf-8 -*-
import logging
import pickle

from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.view import view_config
from pyramid.response import Response
from pyramid import security
from repoze.who.api import get_api as get_who_api

#from .api import get_open_id_consumer, authenticated_user, remember_user, get_return_url
from .api import get_return_url, openid_params

logger = logging.getLogger(__name__)

class RootView(object):
    def __init__(self, request):
        self.request = request

    def login(self):
        return HTTPUnauthorized()

    def verify(self):
        who_api = get_who_api(self.request.environ)
        return_url = get_return_url(self.request)
        identity = openid_params(self.request)
        authenticated, headers = who_api.login(identity)

        if authenticated and return_url:
            res = HTTPFound(location=return_url, headers=headers)
            return res
        else:
            # TODO: デフォルトURLをHostからひいてくる
            res = HTTPFound(location="/")

    def error(self):
        return Response(body="auth error")
        
