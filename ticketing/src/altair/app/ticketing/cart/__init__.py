# -*- coding:utf-8 -*-
import json
#import functools
import logging
import sqlahelper

from pyramid.config import Configurator
#from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.interfaces import IDict
from pyramid.tweens import INGRESS, MAIN, EXCVIEW
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.exceptions import ConfigurationError

from sqlalchemy import engine_from_config

from altair.app.ticketing.wsgi import direct_static_serving_filter_factory

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

def setup_temporary_store(config):
    from datetime import timedelta
    from altair.app.ticketing.interfaces import ITemporaryStore
    from altair.app.ticketing.temp_store import TemporaryCookieStore
    from altair.app.ticketing.cart.models import Cart

    def extra_secret_provider(request, value):
        # master を見ないとダメ
        cart = Cart.query.filter_by(order_no=value).first()
        if cart is None:
            return ''
        else:
            return cart.created_at.isoformat()

    key = config.registry.settings['altair.cart.completion_page.temporary_store.cookie_name']
    secret = config.registry.settings['altair.cart.completion_page.temporary_store.secret']
    timeout_str = config.registry.settings.get('altair.cart.completion_page.temporary_store.timeout')
    timeout = timedelta(seconds=3600)
    if timeout_str is not None:
        try:
            timeout = timedelta(seconds=int(timeout_str))
        except (ValueError, TypeError):
            raise ConfigurationError('altair.cart.completion_page.temporary_store.cookie_timeout')
    config.registry.registerUtility(
        TemporaryCookieStore(
            key=key,
            secret=secret,
            extra_secret_provider=extra_secret_provider,
            max_age=timeout,
            applies_to_route='payment.finish'
            ),
        ITemporaryStore
        )

def setup_components(config):
    from pyramid.interfaces import IRequest
    from .interfaces import IStocker, IReserving, ICartFactory, IPerformanceSelector
    from .stocker import Stocker
    from .reserving import Reserving
    from .carting import CartFactory
    from .performanceselector import MatchUpPerformanceSelector, DatePerformanceSelector, MatchUpPerformanceSelector2
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)
    reg.adapters.register([IRequest], IReserving, "", Reserving)
    reg.adapters.register([IRequest], ICartFactory, "", CartFactory)
    reg.adapters.register([IRequest], IPerformanceSelector, "matchup", MatchUpPerformanceSelector)
    reg.adapters.register([IRequest], IPerformanceSelector, "matchup2", MatchUpPerformanceSelector2)
    reg.adapters.register([IRequest], IPerformanceSelector, "date", DatePerformanceSelector)
    setup_asid(config) # XXX: MOVE THIS
    setup_temporary_store(config)


def setup_asid(config):
    pc = config.registry.settings.get('altair.pc.asid')
    mobile = config.registry.settings.get('altair.mobile.asid')
    smartphone = config.registry.settings.get('altair.smartphone.asid')

    if not pc:
        raise ConfigurationError('altair.pc.asid is not found in settings')
    if not mobile:
        raise ConfigurationError('altair.mobile.asid is not found in settings')
    if not smartphone:
        raise ConfigurationError('altair.smartphone.asid is not found in settings')

    assert config.registry.settings["altair.pc.asid"]
    def altair_pc_asid(request):
        return config.registry.settings["altair.pc.asid"]

    assert config.registry.settings["altair.mobile.asid"]
    def altair_mobile_asid(request):
        return config.registry.settings["altair.mobile.asid"]

    assert config.registry.settings["altair.smartphone.asid"]
    def altair_smartphone_asid(request):
        return config.registry.settings["altair.smartphone.asid"]

    config.set_request_property(altair_pc_asid, "altair_pc_asid", reify=True)
    config.set_request_property(altair_mobile_asid, "altair_mobile_asid", reify=True)
    config.set_request_property(altair_smartphone_asid, "altair_smartphone_asid", reify=True)

def setup_mq(config):
    config.add_publisher_consumer('cart', 'altair.ticketing.cart.mq')

def includeme(config):
    # 購入系
    config.add_route('cart.index', 'events/{event_id}', factory='.resources.compat_ticketing_cart_resource_factory')
    config.add_route('cart.index.sales', 'events/{event_id}/sales/{sales_segment_group_id}', factory='.resources.compat_ticketing_cart_resource_factory')
    config.add_route('cart.index2', 'performances/{performance_id}', factory='.resources.PerformanceOrientedTicketingCartResource')
    config.add_route('cart.index.sales2', 'performances/{performance_id}/sales/{sales_segment_group_id}')
    config.add_route('cart.seat_types', 'events/{event_id}/sales_segment/{sales_segment_id}/seat_types', factory='.resources.EventOrientedTicketingCartResource')
    config.add_route('cart.seat_types2', 'performances/{performance_id}/sales_segment/{sales_segment_id}/seat_types')
    config.add_route('cart.info', 'performances/{performance_id}/sales_segment/{sales_segment_id}/info')
    config.add_route('cart.seats', 'performances/{performance_id}/sales_segment/{sales_segment_id}/seats')
    config.add_route('cart.seat_adjacencies', 'performances/{performance_id}/venues/{venue_id}/seat_adjacencies/{length_or_range}')
    config.add_route('cart.venue_drawing', 'performancess/{performance_id}/venues/{venue_id}/drawing/{part}')
    config.add_route('cart.products', 'events/{event_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products', factory='.resources.EventOrientedTicketingCartResource')

    config.add_route('cart.products2', 'performances/{performance_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products')

    # obsolete
    config.add_route('cart.info.obsolete', 'events/{event_id}/sales_segment/{sales_segment_id}/info', factory='.resources.EventOrientedTicketingCartResource')
    config.add_route('cart.seats.obsolete', 'events/{event_id}/sales_segment/{sales_segment_id}/seats', factory='.resources.EventOrientedTicketingCartResource')
    config.add_route('cart.seat_adjacencies.obsolete', 'events/{event_id}/performances/{performance_id}/venues/{venue_id}/seat_adjacencies/{length_or_range}', factory='.resources.EventOrientedTicketingCartResource')
    config.add_route('cart.venue_drawing.obsolete', 'events/{event_id}/performances/{performance_id}/venues/{venue_id}/drawing/{part}', factory='.resources.EventOrientedTicketingCartResource')
    # order / payment / release
    config.add_route('cart.order', 'order/sales/{sales_segment_id}', factory='.resources.SalesSegmentOrientedTicketingCartResource')
    config.add_route('cart.payment', 'payment/sales/{sales_segment_id}', factory='.resources.SalesSegmentOrientedTicketingCartResource')
    config.add_route('cart.point', 'rsp', factory='.resources.SalesSegmentOrientedTicketingCartResource')
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

    setup_components(config)

def setup_renderers(config):
    import os
    import functools
    from zope.interface import implementer
    from pyramid.interfaces import IRendererFactory
    from pyramid.renderers import RendererHelper
    from pyramid.path import AssetResolver
    from pyramid_selectable_renderer import SelectableRendererFactory
    from altair.app.ticketing.payments.interfaces import IPaymentViewRendererLookup
    from . import selectable_renderer

    @implementer(IPaymentViewRendererLookup)
    class SelectByOrganization(object):
        def __init__(self, selectable_renderer_factory, key_factory):
            self.selectable_renderer_factory = selectable_renderer_factory
            self.key_factory = key_factory

        def __call__(self, path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
            info_ = RendererHelper(
                name=self.key_factory(path_or_renderer_name),
                package=None,
                registry=info.registry
                )
            return self.selectable_renderer_factory(info_)

    @implementer(IPaymentViewRendererLookup)
    class Overridable(object):
        def __init__(self, selectable_renderer_factory, key_factory, resolver):
            self.bad_templates = set()
            self.selectable_renderer_factory = selectable_renderer_factory
            self.key_factory = key_factory
            self.resolver = resolver

        def get_template_path(self, path):
            return '%%(membership)s/plugins/%s' % path

        def __call__(self, path_or_renderer_name, info, for_, plugin_type, plugin_id, **kwargs):
            info_ = RendererHelper(
                self.key_factory(self.get_template_path(path_or_renderer_name)),
                package=None,
                registry=info.registry
                )
            renderer = self.selectable_renderer_factory(info_)

            resolved_uri = "templates/%s" % renderer.implementation().uri # XXX hack: this needs to be synchronized with the value in mako.directories
            if resolved_uri in self.bad_templates:
                return None
            else:
                asset = self.resolver.resolve(resolved_uri)
                if not asset.exists():
                    logger.debug('template %s does not exist' % resolved_uri)
                    self.bad_templates.add(resolved_uri)
                    return None
            return renderer

    config.include(selectable_renderer)

    renderer_factory = functools.partial(
        SelectableRendererFactory,
        selectable_renderer.selectable_renderer.select_fn
        ) # XXX

    config.add_payment_view_renderer_lookup(
        SelectByOrganization(
            renderer_factory,
            selectable_renderer.selectable_renderer
            ),
        'select_by_organization'
        )
    config.add_payment_view_renderer_lookup(
        Overridable(
            renderer_factory,
            selectable_renderer.selectable_renderer,
            AssetResolver(__name__)
            ),
        'overridable'
        )

def import_mail_module(config):
    config.include('altair.app.ticketing.mails')
    config.add_subscriber('.sendmail.on_order_completed', '.events.OrderCompleted')

STATIC_URL_PREFIX = '/static/'
STATIC_ASSET_SPEC = 'altair.app.ticketing.cart:static/'
FC_AUTH_URL_PREFIX = '/fc_auth/static/'
FC_AUTH_STATIC_ASSET_SPEC = "altair.app.ticketing.fc_auth:static/"

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory='.resources.PerformanceOrientedTicketingCartResource',
                          session_factory=session_factory)
    config.registry['sa.engine'] = engine
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'altair.app.ticketing.renderers.csv_renderer_factory')
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={FC_AUTH_STATIC_ASSET_SPEC: FC_AUTH_URL_PREFIX}))
    config.add_static_view(STATIC_URL_PREFIX, STATIC_ASSET_SPEC, cache_max_age=3600)

    ### includes altair.*
    config.include('altair.exclog')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')

    ## mail
    config.include(import_mail_module)

    config.include('.')
    config.include('altair.mq')
    config.include('altair.app.ticketing.qr')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.users')
    from authorization import MembershipAuthorizationPolicy
    config.set_authorization_policy(MembershipAuthorizationPolicy())
    config.add_tween('.tweens.CacheControlTween')
    config.add_tween('.tweens.OrganizationPathTween')
    config.include('altair.app.ticketing.organization_settings')
    config.include('altair.app.ticketing.fc_auth')
    config.include('altair.app.ticketing.checkout')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.mobile')
    config.include('altair.app.ticketing.venues.setup_components')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.add_subscriber('altair.app.ticketing.payments.events.cancel_on_delivery_error',
                          'altair.app.ticketing.payments.events.DeliveryErrorEvent')

    config.set_cart_getter('.api.get_cart_safe')
    config.include('.errors')
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('altair.app.ticketing.cart.tweens.response_time_tween_factory', over=MAIN)
    config.add_tween('altair.app.ticketing.cart.tweens.PaymentPluginErrorConverterTween', under=EXCVIEW)
    config.include(setup_mq)
    config.include(setup_renderers)
    config.scan()

    ## cmsとの通信
    bind_communication_api(config, 
                            "..api.impl.CMSCommunicationApi", 
                            config.registry.settings["altair.cms.api_url"], 
                            config.registry.settings["altair.cms.api_key"]
                            )

    ### s3 assets
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_boto.s3.assets')
    
    ### preview
    config.include(".preview")
    app = config.make_wsgi_app()

    return direct_static_serving_filter_factory({
        STATIC_URL_PREFIX: STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
    })(global_config, app)
