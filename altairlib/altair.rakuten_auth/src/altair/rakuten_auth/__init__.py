# -*- coding:utf-8 -*-
import logging
from pyramid.httpexceptions import HTTPFound
from string import Template
from pyramid import security
from pyramid.config import Configurator

logger = logging.getLogger(__name__)

CONFIG_PREFIX = 'altair.rakuten_auth.'
IDENT_METADATA_KEY = 'altair.rakuten_auth.metadata'
AUTH_PLUGIN_NAME = 'rakuten'

def index(request):
    logger.debug("%s" % request.environ)
    tmpl = Template(u"""
<a href="${login}">Login</a>
Logged in as ${user_id}：${nickname}
<a href="/signout"> signout </a>
""")
    request.response.content_type = 'text/html'
    user_id = security.authenticated_userid(request)

    request.response.text = tmpl.substitute(login=request.route_url('rakuten_auth.login'),
                                            user_id=user_id)
                                  
    return request.response

def signout(request):
    res = HTTPFound(location=request.route_url('top'))
    headers = security.forget(request)
    res.headerlist.extend(headers)
    return res

def includeme(config):
    # openid設定
    settings = config.registry.settings
    config.include(".openid")
    config.include(".oauth")

    config.add_view('.views.RootView', attr="login", route_name="rakuten_auth.login")
    config.add_view('.views.RootView', attr="verify", route_name="rakuten_auth.verify")
    config.add_view('.views.RootView', attr="verify2", route_name="rakuten_auth.verify2")
    config.add_view('.views.RootView', attr="error", route_name="rakuten_auth.error")
    config.add_tween(
        'altair.rakuten_auth.tweens.RakutenAuthTween',
        under=(
            'altair.mobile.tweens.mobile_encoding_convert_factory',
            )
        )

def main(global_conf, **settings):
    """ fot the test """

    config = Configurator(settings=settings)
    config.add_route('top', '/')
    config.add_view('.index', route_name="top")
    config.add_route('signout', '/signout')
    config.add_view('.signout', route_name='signout')
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')

    config.include(".")

    return config.make_wsgi_app()
