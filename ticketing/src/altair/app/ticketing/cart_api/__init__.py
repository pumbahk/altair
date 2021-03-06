# -*- coding:utf-8 -*-
import sqlahelper

from pyramid.config import Configurator
from pyramid.tweens import INGRESS, MAIN, EXCVIEW
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
from ..cart.interfaces import ICartResource
from ..cart.exceptions import CartException
from pyramid.authorization import ACLAuthorizationPolicy
#from ..cart import setup_static_views as cart_setup_static_views
from ..venues import setup_components as venues_setup_components

from altair.pyramid_extra_renderers.json import JSON

def setup_beaker_cache(config):
    from pyramid_beaker import set_cache_regions_from_settings
    set_cache_regions_from_settings(config.registry.settings)

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


def setup_mq(config):
    config.add_publisher_consumer('cart', 'altair.ticketing.cart.mq')
    config.scan('altair.app.ticketing.cart.workers')


def add_metadata(request, value):
    retval = dict()

    environment = request.registry.settings.get('altair.findable_label.label')

    # XXX: should switch in config
    if environment in ['local', 'docker']:
        if 'with_query_dump' in request.GET:
            retval['queries'] = [s for ss in request.environ['altair.queryprofile.statements'].values() for s in ss]
        else:
            retval['num_queries'] = len([s for ss in request.environ['altair.queryprofile.statements'].values() for s in ss])

    if isinstance(value, Exception):
        error = dict(
            exception=value.__class__.__name__,
            message=value.message,
        )

        import traceback
        trace = traceback.format_exc()

        import logging
        logging.getLogger(__name__).warn(trace)

        # XXX: should switch in config
        if environment in ['local', 'docker']:
            error['trace'] = trace

        request.response.status_code = 500
        retval.update(
            error=error,
            environment=environment,
            organization_short_name=request.organization.short_name
        )
    else:
        retval.update(
            data=value,
            environment=environment,
            organization_short_name=request.organization.short_name,
        )
    return retval


class RakutenAuthContext(object):
    def __init__(self, request):
        self.request = request


def decide_auth_types(request, classification):
    if hasattr(request, 'context'):
        context = request.context
        if ICartResource.providedBy(context):
            try:
                return context.cart_setting.auth_types
            except CartException:
                pass
        elif isinstance(context, RakutenAuthContext):
            from altair.rakuten_auth import AUTH_PLUGIN_NAME
            return [AUTH_PLUGIN_NAME]
    return []


def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.fc_auth')
    config.include('altair.app.ticketing.extauth.userside_impl')

    config.set_who_api_decider(decide_auth_types)
    from altair.auth import set_auth_policy
    from altair.app.ticketing.security import AuthModelCallback
    set_auth_policy(config, AuthModelCallback(config))
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # 楽天認証URL
    config.add_route('rakuten_auth.verify', '/verify', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.verify2', '/verify2', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.error', '/error', factory=RakutenAuthContext)
    config.add_route('cart.logout', '/logout')

    # キーワード認証＆外部会員番号取得キーワード認証
    # altair.app.ticketing.authentication の認証プラグインは
    # 新カートでも再認証しないと認証情報を取得できないので読み込みます。
    config.include('altair.app.ticketing.authentication')


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
    setup_beaker_cache(config)
    config.include('pyramid_tm')
    config.include('pyramid_dogpile_cache')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.mq')
    config.include('altair.sqlahelper')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.app.ticketing.cart.request')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_boto.s3.assets')
    config.include(setup_components)
    config.include(setup_auth)
    config.include(setup_mq)
    config.include(venues_setup_components)
    config.include('altair.app.ticketing.setup_beaker_cache')

    config.add_route('cart.api.health_check', '/')
    config.add_route('cart.api.index', '/api/v1/', request_method='GET')
    config.add_route('cart.api.performances', '/api/v1/events/{event_id}/performances', request_method='GET', factory="altair.app.ticketing.cart.resources.EventOrientedTicketingCartResource")
    config.add_route('cart.api.performance', '/api/v1/performances/{performance_id}', request_method='GET')
    config.add_route('cart.api.stock_types', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/stock_types', request_method='GET')
    config.add_route('cart.api.stock_type', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/stock_types/{stock_type_id:\d+}', request_method='GET', factory="altair.app.ticketing.cart.resources.SalesSegmentOrientedTicketingCartResource")
    config.add_route('cart.api.stock_type.all', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/stock_types/all', request_method='GET', factory="altair.app.ticketing.cart.resources.SalesSegmentOrientedTicketingCartResource")
    config.add_route('cart.api.seats', '/api/v1/performances/{performance_id}/seats', request_method='GET')
    config.add_route('cart.api.seat_reserve', '/api/v1/performances/{performance_id}/sales_segments/{sales_segment_id}/seats/reserve', request_method='POST', factory="altair.app.ticketing.cart.resources.SalesSegmentOrientedTicketingCartResource")
    config.add_route('cart.api.seat_release', '/api/v1/performances/{performance_id}/seats/release', request_method='POST')
    config.add_route('cart.api.select_products', '/api/v1/performances/{performance_id}/select_products', request_method='POST')

    config.scan('.views')

    import os
    import newrelic.agent
    app = config.make_wsgi_app()
    newrelic_conf_file_path = '/etc/newrelic/altair.ticketing.cart.api.newrelic.ini'
    if os.path.isfile(newrelic_conf_file_path):
        newrelic.agent.initialize(newrelic_conf_file_path)
        app = newrelic.agent.WSGIApplicationWrapper(app)

    return app
