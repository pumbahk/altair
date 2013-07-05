# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
#from repoze.who.api import get_api as get_who_api
from altair.auth import who_api as get_who_api
from pyramid.view import view_config
from ticketing.cart import api as cart_api
from ticketing.core import api as core_api
from . import SESSION_KEY

logger = logging.getLogger(__name__)

class LoginView(object):
    renderer_tmpl = "ticketing.fc_auth:templates/{membership}/login.html"
    renderer_tmpl_mobile = "ticketing.fc_auth:templates/{membership}/login_mobile.html"

    def __init__(self, request):
        self.request = request
        self.context = request.context


    def select_renderer(self, membership):
        if cart_api.is_mobile(self.request):
            self.request.override_renderer = self.renderer_tmpl_mobile.format(membership=membership)
        else:
            self.request.override_renderer = self.renderer_tmpl.format(membership=membership)

    @property
    def return_to_url(self):
        return self.request.session.get(SESSION_KEY, {}).get('return_url') or core_api.get_host_base_url(self.request)

    @view_config(request_method="GET", route_name='fc_auth.login', renderer='json')
    def login_form(self):
        membership = self.request.matchdict['membership']
        self.select_renderer(membership)
        return dict(username='')


    @view_config(request_method="POST", route_name='fc_auth.login', renderer='string')
    def login(self):
        who_api = get_who_api(self.request.environ, name="fc_auth")
        membership = self.request.matchdict['membership']
        username = self.request.params['username']
        password = self.request.params['password']
        logger.debug("authenticate for membership %s" % membership)

        identity = {
            'membership': membership,
            'username': username,
            'password': password,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership)
            return {'username': username,
                    'message': u'会員番号かパスワードが一致しません'}


        return_to_url = self.return_to_url 
        res = HTTPFound(location=return_to_url, headers=headers)


        return res

    @view_config(request_method="POST", route_name='fc_auth.guest', renderer='string')
    def guest_login(self):
        who_api = get_who_api(self.request.environ, name="fc_auth")
        membership = self.request.matchdict['membership']
        logger.debug("guest authenticate for membership %s" % membership)

        identity = {
            'membership': membership,
            'is_guest': True,
        }
        authenticated, headers = who_api.login(identity)

        if authenticated is None:
            self.select_renderer(membership)
            return {'username': '',
                    'guest_message': u''}


        return_to_url = self.return_to_url
        res = HTTPFound(location=return_to_url, headers=headers)

        return res

