# -*- coding:utf-8 -*-
import logging
from string import Template

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .interfaces import IRakutenOpenID
from .api import RakutenOpenID, authenticated_user

logger = logging.getLogger(__name__)

def index(request):
    logger.debug("%s" % request.environ)
    tmpl = Template(u"""
<a href="${login}">Login</a>
Logged in as ${user_id}
""")
    request.response.content_type = 'text/html'
    
    request.response.text = tmpl.substitute(login=request.route_url('login'),
                                            user_id=authenticated_user(request))
    return request.response

def includeme(config):
    # openid設定
    settings = config.registry.settings
    base_url = settings['altaircms.openid.base_url']
    return_to = settings['altaircms.openid.return_to']
    consumer_key = settings['altaircms.openid.consumer_key']
    secret = settings['altaircms.openid.secret']

    reg = config.registry
    reg.registerUtility(RakutenOpenID(
            base_url=base_url,
            return_to=return_to,
            consumer_key=consumer_key,
            secret=secret,
            ),
                        IRakutenOpenID)

    config.add_view('.views.RootView', attr="login", route_name="login")
    config.add_view('.views.RootView', attr="verify", route_name="verify")
    

def main(global_conf, **settings):
    """ fot the test """

    config = Configurator(settings=settings,
                          authorization_policy=ACLAuthorizationPolicy(),
                          authentication_policy=AuthTktAuthenticationPolicy("secret"))
    config.add_route('top', '/')
    config.add_route('login', '/login')
    config.add_route('verify', '/verify')
    config.add_view('.index', route_name="top")

    config.include(".")

    return config.make_wsgi_app()
