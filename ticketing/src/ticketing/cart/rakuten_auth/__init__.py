# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from string import Template
from pyramid import security
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from .interfaces import IRakutenOpenID
from .api import RakutenOpenID, authenticated_user

logger = logging.getLogger(__name__)

def index(request):
    logger.debug("%s" % request.environ)
    tmpl = Template(u"""
<a href="${login}">Login</a>
Logged in as ${user_id}：${nickname}
<a href="/signout"> signout </a>
""")
    request.response.content_type = 'text/html'
    user = authenticated_user(request)

    request.response.text = tmpl.substitute(login=request.route_url('rakuten_auth.login'),
                                            user_id=user['clamed_id'] if user else '',
                                            nickname=user['nickname'] if user else '')
                                  
    return request.response

def signout(request):
    res = HTTPFound(location=request.route_url('top'))
    headers = security.forget(request)
    res.headerlist.extend(headers)
    return res

def includeme(config):
    # openid設定
    settings = config.registry.settings
    who_config = settings['pyramid_who.config']

    config.add_view('.views.RootView', attr="login", route_name="rakuten_auth.login")
    config.add_view('.views.RootView', attr="verify", route_name="rakuten_auth.verify")
    config.add_view('.views.RootView', attr="error", route_name="rakuten_auth.error")
    config.set_forbidden_view('.views.RootView', attr="login")
    
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_authentication_policy(WhoV2AuthenticationPolicy(who_config, 'auth_tkt'))

def main(global_conf, **settings):
    """ fot the test """

    config = Configurator(settings=settings)
    config.add_route('top', '/')
    config.add_view('.index', route_name="top")
    config.add_route('signout', '/signout')
    config.add_view('.signout', route_name='signout')
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('akuten_auth.error', '/verify')

    config.include(".")

    return config.make_wsgi_app()
