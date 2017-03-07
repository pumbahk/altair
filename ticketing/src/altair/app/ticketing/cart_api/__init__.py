# -*- coding:utf-8 -*-
import sqlahelper

from pyramid.config import Configurator
from pyramid.tweens import INGRESS, MAIN, EXCVIEW
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from altair.pyramid_extra_renderers.json import JSON


def setup_tweens(config):
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('.tweens.OrganizationPathTween', over=EXCVIEW)
    config.add_tween('.tweens.response_time_tween_factory', over=MAIN)
    config.add_tween('.tweens.PaymentPluginErrorConverterTween', under=EXCVIEW)
    config.add_tween('.tweens.CacheControlTween')


def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='altair.app.ticketing.cart.resources.PerformanceOrientedTicketingCartResource'
        )

    config.add_renderer('json', JSON())
    config.include('pyramid_tm')
    config.include('pyramid_dogpile_cache')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.sqlahelper')
    config.include('altair.app.ticketing.cart.request')
    config.add_route('cart.api.health_check', '/')
    config.add_route('cart.api.index', '/api/v1/', request_method='GET')
    config.add_route('cart.api.performances', '/api/v1/events/{event_id}/performances', request_method='GET', factory="altair.app.ticketing.cart.resources.EventOrientedTicketingCartResource")
    config.add_route('cart.api.performance', '/api/v1/performances/{performance_id}', request_method='GET')
    config.add_route('cart.api.stock_types', '/api/v1/performances/{performance_id}/stock_types', request_method='GET')
    config.add_route('cart.api.stock_type', '/api/v1/stock_types/{stock_type_id}', request_method='GET')
    config.add_route('cart.api.seats', '/api/v1/performances/{performance_id}/seats', request_method='GET')
    config.add_route('cart.api.seat_reserve', '/api/v1/performances/{performance_id}/seats/reserve', request_method='GET')
    config.add_route('cart.api.seat_release', '/api/v1/performances/{performance_id}/seats/release', request_method='GET')

    config.scan('.views')

    return config.make_wsgi_app()
