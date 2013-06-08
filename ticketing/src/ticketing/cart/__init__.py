# -*- coding:utf-8 -*-
import json
#import functools
import logging
import sqlahelper

from pyramid.config import Configurator
#from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.interfaces import IDict
from pyramid.tweens import INGRESS
from pyramid_beaker import (
    session_factory_from_settings,
    set_cache_regions_from_settings,
    )


from sqlalchemy import engine_from_config

logger = logging.getLogger(__name__)

from ..api.impl import bind_communication_api ## cmsとの通信

### pc smartphone switch
from altair.mobile import PC_ACCESS_COOKIE_NAME
PC_SWITCH_COOKIE_NAME = PC_ACCESS_COOKIE_NAME

def exception_message_renderer_factory(show_traceback):
    def exception_message_renderer(request, exc_info, message):
        from pyramid.httpexceptions import HTTPInternalServerError
        from pyramid.renderers import render
        from .selectable_renderer import selectable_renderer
        from altair.mobile.api import is_mobile
        if is_mobile(request):
            renderer = selectable_renderer('carts_mobile/%(membership)s/error.html')
        else:
            renderer = selectable_renderer('carts/%(membership)s/message.html')
        return HTTPInternalServerError(body=render(renderer, { 'message': u'システムエラーが発生しました。大変お手数ですが、しばらく経ってから再度トップ画面よりアクセスしてください。(このURLに再度アクセスしてもエラーが出続けることがあります)' }, request))
    return exception_message_renderer

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        if self.request.organization:
            return self.request.organization.setting.auth_type
        else:
            return 'fc_auth'

def add_routes(config):
    # 購入系
    config.add_route('cart.index', 'events/{event_id}')
    config.add_route('cart.index.sales', 'events/{event_id}/sales/{sales_segment_group_id}')
    config.add_route('cart.seat_types', 'events/{event_id}/sales_segment/{sales_segment_id}/seat_types')
    config.add_route('cart.info', 'events/{event_id}/sales_segment/{sales_segment_id}/info')
    config.add_route('cart.seats', 'events/{event_id}/sales_segment/{sales_segment_id}/seats')
    config.add_route('cart.seat_adjacencies', 'events/{event_id}/performances/{performance_id}/venues/{venue_id}/seat_adjacencies/{length_or_range}')
    config.add_route('cart.venue_drawing', 'events/{event_id}/performances/{performance_id}/venues/{venue_id}/drawing/{part}')
    config.add_route('cart.products', 'events/{event_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products')

    # obsolete
    config.add_route('cart.seat_types.obsolete', 'events/{event_id}/performances/{performance_id}/sales_segment/{sales_segment_id}/seat_types')
    config.add_route('cart.seats.obsolete', 'events/{event_id}/performances/{performance_id}/sales_segment/{sales_segment_id}/seats')
    config.add_route('cart.products.obsolete', 'events/{event_id}/performances/{performance_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products')

    # order / payment / release
    config.add_route('cart.order', 'order/sales/{sales_segment_id}')
    config.add_route('cart.payment', 'payment/sales/{sales_segment_id}')
    config.add_route('cart.release', 'release')
    config.add_route('cart.logout', 'logout')

    # 完了／エラー
    config.add_route('payment.confirm', 'confirm')
    config.add_route('payment.finish', 'completed')

    # PC/Smartphone切替
    config.add_route('cart.switchpc', 'switchpc/{event_id}')
    config.add_route('cart.switchsp', 'switchsp/{event_id}')
    config.add_route('cart.switchpc.perf', 'switchpc/{event_id}/{performance}')
    config.add_route('cart.switchsp.perf', 'switchsp/{event_id}/{performance}')

def add_rakuten_auth_routes(config):
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')

def setup_cart_adapters(config):
    from pyramid.interfaces import IRequest
    from .interfaces import IStocker, IReserving, ICartFactory
    from .stocker import Stocker
    from .reserving import Reserving
    from .carting import CartFactory
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)

def setup_performance_selector(config):
    from pyramid.interfaces import IRequest
    from .interfaces import IPerformanceSelector
    from .performanceselector import MatchUpPerformanceSelector, DatePerformanceSelector
    reg = config.registry
    reg.adapters.register([IRequest], IPerformanceSelector, "matchup", MatchUpPerformanceSelector)
    reg.adapters.register([IRequest], IPerformanceSelector, "date", DatePerformanceSelector)

def includeme(config):
    # ディレクティブ
    config.add_directive("add_payment_method", ".directives.add_payment_method")

    config.include(setup_cart_adapters)

    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool,
                                isolation_level='READ COMMITTED',
                                pool_recycle=60)
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory='.resources.TicketingCartResource',
                          session_factory=session_factory)
    config.registry['sa.engine'] = engine

    from ticketing import setup_standard_renderers
    config.include(setup_standard_renderers)

    config.add_static_view('static', 'ticketing.cart:static', cache_max_age=3600)

    ## includes altair.*
    config.include("altair.cdnpath")
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.mobile')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_boto.s3.assets')
    config.include('altair.rakuten_auth')

    ## includes ticketing.*
    config.include('ticketing.cart.selectable_renderer')
    config.include('ticketing.qr')
    config.include('ticketing.users')
    config.include('ticketing.mails')
    config.include('ticketing.organization_settings')
    config.include('ticketing.fc_auth')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('ticketing.venues')
    config.include('ticketing.payments')
    config.include('ticketing.payments.plugins')

    ## includes .
    config.include('.')
    config.include('.errors')
    config.include(".selectable_renderer")
    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    ## routes & views
    config.include(setup_performance_selector)
    config.include(add_routes)
    config.include(add_rakuten_auth_routes)
    config.scan('.views')
    config.scan('.mobile_views')

    ## tweens
    config.add_tween('ticketing.cart.tweens.altair_host_tween_factory',
        under='altair.mobile.tweens.mobile_encoding_convert_factory',
        over='altair.auth.activate_who_api_tween')
    config.add_tween('ticketing.tweens.CacheControlTween')
    config.add_tween('ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('ticketing.cart.tweens.response_time_tween_factory', under=INGRESS)

    config.set_cart_getter('.api.get_cart_safe')

    ## auth
    from authorization import MembershipAuthorizationPolicy
    config.set_authorization_policy(MembershipAuthorizationPolicy())

    ## cdnpath
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={"ticketing.fc_auth:static/": "/fc_auth/static/"}))


    ## cmsとの通信
    bind_communication_api(config, 
                            "..api.impl.CMSCommunicationApi", 
                            config.registry.settings["altaircms.event.notification_url"], 
                            config.registry.settings["altaircms.apikey"]
                            )

    ## events
    config.add_subscriber('.sendmail.on_order_completed', '.events.OrderCompleted')
    config.add_subscriber('ticketing.payments.events.cancel_on_delivery_error',
                          'ticketing.payments.events.DeliveryErrorEvent')

    return config.make_wsgi_app()
