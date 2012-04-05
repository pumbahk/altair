# -*- coding:utf-8 -*-
from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import authenticated_userid, remember
from .interfaces import IRakutenOpenID
from .api import RakutenOpenID, get_open_id_consumer

from string import Template

import logging

logger = logging.getLogger(__name__)

class RootView(object):
    def __init__(self, request):
        self.request = request

    @property
    def consumer(self):
        return get_open_id_consumer(self.request)

    @view_config(route_name='top')
    def index(self):
        logger.debug("%s" % self.request.environ)
        tmpl = Template(u"""
<a href="${login}">Login</a>
Logged in as ${user_id}
""")
        self.request.response.content_type = 'text/html'

        self.request.response.text = tmpl.substitute(login=self.request.route_url('login'),
                                                     user_id=authenticated_userid(self.request))
        return self.request.response

    @view_config(route_name="login")
    def login(self):
        url = self.consumer.get_redirect_url()
        tmpl = Template(u"""
<a href="${login}">Login</a>
""")
        self.request.response.content_type = 'text/html'

        self.request.response.text = tmpl.substitute(login=url)
        return self.request.response

    @view_config(route_name="verify")
    def verify(self):
        logger.debug("verify")
        clamed_url = self.consumer.verify_authentication(self.request)
        if clamed_url:
            headers = remember(self.request, clamed_url)
            self.request.response.headerlist.extend(headers)

        self.request.response.text = u"%s" % clamed_url

        return self.request.response

def includeme(config):
    # openid設定
    settings = config.registry.settings
    base_url = settings['altaircms.openid.base_url']
    return_to = settings['altaircms.openid.return_to']
    consumer_key = settings['altaircms.openid.consumer_key']

    reg = config.registry
    reg.registerUtility(RakutenOpenID(
            base_url=base_url,
            return_to=return_to,
            consumer_key=consumer_key,
            ),
                        IRakutenOpenID)
    

def main(global_conf, **settings):
    config = Configurator(settings=settings,
                          authorization_policy=ACLAuthorizationPolicy(),
                          authentication_policy=AuthTktAuthenticationPolicy("secret"))
    config.add_route('top', '/')
    config.add_route('login', '/login')
    config.add_route('verify', '/verify')

    config.include(".")
    config.scan()
    return config.make_wsgi_app()
