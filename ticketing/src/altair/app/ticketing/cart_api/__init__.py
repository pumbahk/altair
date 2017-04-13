# -*- coding:utf-8 -*-
import sqlahelper

from pyramid.config import Configurator
from pyramid.tweens import INGRESS, MAIN, EXCVIEW
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool

from altair.pyramid_extra_renderers.json import JSON


def setup_components(config):
    from pyramid.interfaces import IRequest
    from altair.app.ticketing.cart.interfaces import IStocker, IReserving, ICartFactory, IPerformanceSelector
    from altair.app.ticketing.cart.stocker import Stocker
    from altair.app.ticketing.cart.reserving import Reserving
    from altair.app.ticketing.cart.carting import CartFactory
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)

def setup_tweens(config):
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('.tweens.OrganizationPathTween', over=EXCVIEW)
    config.add_tween('.tweens.response_time_tween_factory', over=MAIN)
    config.add_tween('.tweens.PaymentPluginErrorConverterTween', under=EXCVIEW)
    config.add_tween('.tweens.CacheControlTween')

def add_metadata(request, value):
    return dict(
        data=value,
        environment=request.registry.settings.get('altair.findable_label.label'),
        organization_short_name=request.organization.short_name
    )

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='altair.app.ticketing.cart.resources.PerformanceOrientedTicketingCartResource'
        )

    config.add_renderer('json', JSON(metadata_handler=add_metadata))
    config.include('pyramid_tm')
    config.include('pyramid_dogpile_cache')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.sqlahelper')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.app.ticketing.cart.request')
    config.include(setup_components)

    config.add_route('cart.api.health_check', '/')
    config.add_route('cart.api.index', '/api/v1/', request_method='GET')
    config.add_route('cart.api.performances', '/api/v1/events/{event_id}/performances', request_method='GET', factory="altair.app.ticketing.cart.resources.EventOrientedTicketingCartResource")
    config.add_route('cart.api.performance', '/api/v1/performances/{performance_id}', request_method='GET')
    config.add_route('cart.api.stock_types', '/api/v1/performances/{performance_id}/stock_types', request_method='GET')
    config.add_route('cart.api.stock_type', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/stock_types/{stock_type_id}', request_method='GET', factory="altair.app.ticketing.cart.resources.SalesSegmentOrientedTicketingCartResource")
    config.add_route('cart.api.seats', '/api/v1/performances/{performance_id}/seats', request_method='GET')
    config.add_route('cart.api.seat_reserve', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/seats/reserve', request_method='POST', factory="altair.app.ticketing.cart.resources.SalesSegmentOrientedTicketingCartResource")
    config.add_route('cart.api.seat_release', '/api/v1/performances/{performance_id}/seats/release', request_method='POST')
    config.add_route('cart.api.select_product', '/api/v1/performances/{performance_id}/seat/select_product', request_method='POST')

    config.scan('.views')

    return config.make_wsgi_app()
