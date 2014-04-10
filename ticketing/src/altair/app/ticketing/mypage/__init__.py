# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid_who.whov2 import WhoV2AuthenticationPolicy
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    config.add_route('mypage.index', '/')
    config.add_route('mypage.logout', '/logout')
    config.add_route('mypage.order', '/order/{order_id}')
    config.add_route('mypage.qr_print', '/order/qr/print')
    config.add_route('mypage.qr_send', '/order/qr/send')
    config.add_route('qr.draw', '/qr/{ticket_id}/{sign}/image')

    config.add_subscriber('altair.app.ticketing.cart.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='.resources.TicketingMyPageResources'
        )
    config.registry['sa.engine'] = engine

    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'altair.app.ticketing.renderers.csv_renderer_factory')
    config.add_static_view('img', 'altair.app.ticketing.cart:static', cache_max_age=3600)

    config.include('altair.app.ticketing.setup_beaker_cache')
    config.include('.')
    config.include('.errors')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.users')
    who_config = settings['pyramid_who.config']
    from ..cart.authorization import MembershipAuthorizationPolicy
    config.set_authorization_policy(MembershipAuthorizationPolicy())
    from ..cart.security import auth_model_callback
    config.set_authentication_policy(WhoV2AuthenticationPolicy(who_config, 'auth_tkt', callback=auth_model_callback))
    config.scan()
    config.scan('..core.models')

    return config.make_wsgi_app()
