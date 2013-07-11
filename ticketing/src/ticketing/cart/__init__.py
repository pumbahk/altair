# -*- coding:utf-8 -*-
import json
#import functools
import logging
import sqlahelper

from ticketing.models import DBSession
from pyramid.config import Configurator
#from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.interfaces import IDict
from pyramid.tweens import INGRESS
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings


from sqlalchemy import engine_from_config

from ticketing.core.api import get_organization

logger = logging.getLogger(__name__)


from ..api.impl import bind_communication_api ## cmsとの通信

### pc smartphone switch
from altair.mobile import PC_ACCESS_COOKIE_NAME
PC_SWITCH_COOKIE_NAME = PC_ACCESS_COOKIE_NAME

def exception_message_renderer_factory(show_traceback):
    def exception_message_renderer(request, exc_info, message):
        from pyramid.httpexceptions import HTTPInternalServerError
        from pyramid.renderers import render
        from pyramid import security
        from .selectable_renderer import selectable_renderer
        from altair.mobile.api import is_mobile
        if is_mobile(request):
            renderer = selectable_renderer('%(membership)s/mobile/error.html')
        else:
            renderer = selectable_renderer('%(membership)s/pc/message.html')
        return HTTPInternalServerError(body=render(renderer, { 'message': u'システムエラーが発生しました。大変お手数ですが、しばらく経ってから再度トップ画面よりアクセスしてください。(このURLに再度アクセスしてもエラーが出続けることがあります)' }, request), headers=security.forget(request))
    return exception_message_renderer

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        #return self.request.organization.setting.auth_type
        org = get_organization(self.request)
        DBSession.add(org) # XXX
        return org.setting.auth_type


def includeme(config):
    # ディレクティブ
    config.add_directive("add_payment_method", ".directives.add_payment_method")
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

    # 完了／エラー
    config.add_route('payment.confirm', 'confirm')
    config.add_route('payment.finish', 'completed')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    # PC/Smartphone切替
    config.add_route('cart.switchpc', 'switchpc/{event_id}')
    config.add_route('cart.switchsp', 'switchsp/{event_id}')
    config.add_route('cart.switchpc.perf', 'switchpc/{event_id}/{performance}')
    config.add_route('cart.switchsp.perf', 'switchsp/{event_id}/{performance}')

    # 楽天認証URL
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')
    config.add_route('cart.logout', '/logout')

    from pyramid.interfaces import IRequest
    from .interfaces import IStocker, IReserving, ICartFactory, IPerformanceSelector
    from .stocker import Stocker
    from .reserving import Reserving
    from .carting import CartFactory
    from .performanceselector import MatchUpPerformanceSelector, DatePerformanceSelector
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    reg.adapters.register([IRequest], IPerformanceSelector, "matchup", MatchUpPerformanceSelector)
    reg.adapters.register([IRequest], IPerformanceSelector, "date", DatePerformanceSelector)

def import_mail_module(config):
    config.include("ticketing.mails")
    config.add_subscriber('.sendmail.on_order_completed', '.events.OrderCompleted')

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
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={"ticketing.fc_auth:static/": "/fc_auth/static/"}))
    config.add_static_view('static', 'ticketing.cart:static', cache_max_age=3600)

    ### includes altair.*
    config.include('altair.exclog')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')

    ### selectable renderer
    config.include(".selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)

    ## mail
    config.include(import_mail_module)

    config.include('.')
    config.include("ticketing.qr")
    config.include('altair.rakuten_auth')
    config.include('ticketing.users')
    from authorization import MembershipAuthorizationPolicy
    config.set_authorization_policy(MembershipAuthorizationPolicy())
    config.add_tween('.tweens.CacheControlTween')
    config.add_tween('.tweens.OrganizationPathTween')
    config.include('ticketing.organization_settings')
    config.include('ticketing.fc_auth')
    config.include('ticketing.checkout')
    config.include('ticketing.multicheckout')
    config.include('altair.mobile')
    config.include("ticketing.venues")
    config.include("ticketing.payments")
    config.include('ticketing.payments.plugins')
    config.add_subscriber('ticketing.payments.events.cancel_on_delivery_error',
                          'ticketing.payments.events.DeliveryErrorEvent')

    config.set_cart_getter('.api.get_cart_safe')
    config.include('.errors')
    config.add_tween('ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('ticketing.cart.tweens.response_time_tween_factory', under=INGRESS)
    config.scan()



    ## cmsとの通信
    bind_communication_api(config, 
                            "..api.impl.CMSCommunicationApi", 
                            config.registry.settings["altaircms.event.notification_url"], 
                            config.registry.settings["altaircms.apikey"]
                            )

    ### s3 assets
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_boto.s3.assets')

    return config.make_wsgi_app()
