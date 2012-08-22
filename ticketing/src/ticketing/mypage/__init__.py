# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid_beaker import session_factory_from_settings

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('mypage.index', '/')
    config.add_route('mypage.logout', '/logout')
    config.add_route('mypage.order', '/order/{order_id}')

    config.add_subscriber('ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.error', '/error')

def main(global_config, **settings):
    engine = engine_from_config(settings)
    my_session_factory = session_factory_from_settings(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.set_root_factory('.resources.TicketingMyPageResources')
    config.registry['sa.engine'] = engine

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)

    config.include('.')
    config.include('.errors')
    config.include('..cart.rakuten_auth')
    who_config = settings['pyramid_who.config']
    from ..cart.authorization import MembershipAuthorizationPolicy
    config.set_authorization_policy(MembershipAuthorizationPolicy())
    from ..cart.security import auth_model_callback
    config.set_authentication_policy(WhoV2AuthenticationPolicy(who_config, 'auth_tkt', callback=auth_model_callback))
    config.scan()
    config.scan('..core.models')

    return config.make_wsgi_app()
