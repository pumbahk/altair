# -*- coding:utf-8 -*-
import logging
#import pickle
from datetime import datetime
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
#from pyramid.view import view_config
from pyramid.response import Response
from pyramid import security
from repoze.who.api import get_api as get_who_api

#from .api import get_open_id_consumer, authenticated_user, remember_user, get_return_url
from .api import get_return_url, openid_params, tokenize

logger = logging.getLogger(__name__)



class RootView(object):

    def __init__(self, request):
        self.request = request

    def login(self):
        return HTTPUnauthorized()

    def verify(self):
        who_api = get_who_api(self.request.environ)
        identity = openid_params(self.request)
        authenticated, headers = who_api.login(identity)

        if authenticated:
            authenticated = authenticated['repoze.who.userid']
            now = datetime.now()
            nonce = now.strftime('%Y%m%d:%H%M')
            token = tokenize(self.request, nonce, authenticated)
            res = HTTPFound(location=self.request.route_url('rakuten_auth.verify2', _query={"authenticated": authenticated, "nonce": nonce, "token": token}))
            return res
        else:
            # TODO: デフォルトURLをHostからひいてくる
            res = HTTPFound(location="/")

    def error(self):
        return Response(body="auth error")
        

    def verify2(self):
        authenticated = self.request.params['authenticated']
        nonce = self.request.params['nonce']
        remote_token = self.request.params['token']

        token = tokenize(self.request, nonce, authenticated)


        if remote_token == token:

            headers = security.remember(self.request, authenticated)
            return_url = get_return_url(self.request)
            res = HTTPFound(location=return_url, headers=headers)
            return res

        else:
            return self.error()
