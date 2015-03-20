# -*- coding:utf-8 -*-
import json
import logging
import sqlahelper
import urllib

from pyramid.config import Configurator
from pyramid.compat import string_types
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.renderers import RendererHelper
from pyramid.interfaces import IDict
from pyramid.tweens import INGRESS, MAIN, EXCVIEW
from pyramid.exceptions import ConfigurationError

from sqlalchemy import engine_from_config

from altair.app.ticketing.wsgi import direct_static_serving_filter_factory
from altair.mobile import PC_ACCESS_COOKIE_NAME

from .interfaces import ICartResource
from ..api.impl import bind_communication_api ## cmsとの通信

logger = logging.getLogger(__name__)


PC_SWITCH_COOKIE_NAME = PC_ACCESS_COOKIE_NAME

CART_STATIC_URL_PREFIX = '/static/'
CART_CDN_URL_PREFIX = '/cart/static/'
CART_STATIC_ASSET_SPEC = 'altair.app.ticketing.cart:static/'
FC_AUTH_URL_PREFIX = '/static.fc_auth/'
FC_AUTH_CDN_URL_PREFIX = '/fc_auth/static/'
FC_AUTH_STATIC_ASSET_SPEC = "altair.app.ticketing.fc_auth:static/"


def empty_resource_factory(request):
    return None

def exception_message_renderer_factory(show_traceback):
    def exception_message_renderer(request, exc_info, message):
        from pyramid.httpexceptions import HTTPInternalServerError
        from pyramid.renderers import render
        from pyramid import security
        from .rendering import selectable_renderer
        from altair.mobile.api import is_mobile_request
        renderer = selectable_renderer('error.html')
        return HTTPInternalServerError(body=render(renderer, { 'message': u'システムエラーが発生しました。大変お手数ですが、しばらく経ってから再度トップ画面よりアクセスしてください。(このURLに再度アクセスしてもエラーが出続けることがあります)' }, request), headers=security.forget(request))
    return exception_message_renderer

def setup_temporary_store(config):
    from datetime import timedelta
    from altair.app.ticketing.interfaces import ITemporaryStore
    from altair.app.ticketing.temp_store import TemporaryCookieStore
    from altair.app.ticketing.orders.models import Order
    from altair.app.ticketing.cart.models import Cart

    def extra_secret_provider(request, value):
        # master を見ないとダメ
        cart = Cart.query.join(Cart.order).filter(Order.order_no == value).first()
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

def setup_mq(config):
    config.add_publisher_consumer('cart', 'altair.ticketing.cart.mq')
    config.scan('.workers')

def setup_payment_renderers(config):
    from zope.interface import implementer
    from altair.app.ticketing.payments.interfaces import IPaymentViewRendererLookup
    from . import rendering, api
    from .interfaces import ICartResource

    @implementer(IPaymentViewRendererLookup)
    class SelectByOrganization(object):
        def __init__(self, selectable_renderer_helper_factory):
            self.selectable_renderer_helper_factory = selectable_renderer_helper_factory

        def __call__(self, request, path_or_renderer_name, for_, plugin_type, plugin_id, package, registry, **kwargs):
            if isinstance(path_or_renderer_name, string_types) and \
               '.' in path_or_renderer_name and \
               ':' not in path_or_renderer_name and \
               ICartResource.providedBy(request.context):
                if api.is_booster_cart(request.context.cart_setting):
                    path_or_renderer_name = 'booster/' + path_or_renderer_name
                elif api.is_fc_cart(request.context.cart_setting):
                    path_or_renderer_name = 'fc/' + path_or_renderer_name
            return self.selectable_renderer_helper_factory(
                path_or_renderer_name,
                package,
                registry,
                request=request,
                **kwargs
                )

    @implementer(IPaymentViewRendererLookup)
    class DynamicRendererHelperFactoryAdapter(object):
        def __init__(self, renderer_helper_factory):
            self.renderer_helper_factory = renderer_helper_factory

        def __call__(self, request, path_or_renderer_name, for_, plugin_type, plugin_id, package, registry, **kwargs):
            return self.renderer_helper_factory(path_or_renderer_name, package=package, registry=registry, request=request)

    config.add_payment_view_renderer_lookup(
        SelectByOrganization(
            rendering.selectable_renderer_helper_factory
            ),
        'select_by_organization'
        )
    config.add_payment_view_renderer_lookup(
        DynamicRendererHelperFactoryAdapter(
            rendering.OverridableTemplateRendererHelperFactory(
                config.registry.__name__,
                lambda name, package, registry, request, **kwargs: request.view_context,
                [
                    'templates/%(organization_short_name)s/%(ua_type)s/plugins/%(path)s',
                    'templates/%(organization_short_name)s/plugins/%(path)s',
                    'templates/__default__/%(ua_type)s/plugins/%(path)s',
                    'templates/__default__/plugins/%(path)s',
                    '%(their_package)s:templates/%(ua_type)s/%(path)s',
                    ]
                )
            ),
        'overridable'
        )

def import_mail_module(config):
    config.include('altair.app.ticketing.mails')
    config.add_subscriber('.sendmail.on_order_completed', '.events.OrderCompleted')


def decide_auth_types(request, classification):
    if hasattr(request, 'context'):
        context = request.context
        if ICartResource.providedBy(context):
            return context.cart_setting.auth_types
    return []

def setup_nogizaka_auth(config):
    config.include('altair.app.ticketing.project_specific.nogizaka46.auth')
    config.add_nogizaka_entrypoint('cart.index')
    config.add_nogizaka_entrypoint('cart.index2')
    config.add_nogizaka_entrypoint('cart.index.sales')
    config.add_nogizaka_entrypoint('cart.agreement')
    config.add_nogizaka_entrypoint('cart.agreement2')
    config.add_nogizaka_entrypoint('cart.agreement.compat')
    config.add_nogizaka_entrypoint('cart.agreement2.compat')

def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.fc_auth')

    config.set_who_api_decider(decide_auth_types)
    from altair.auth import set_auth_policy
    set_auth_policy(config, 'altair.app.ticketing.security:auth_model_callback')
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # 楽天認証URL
    config.add_route('rakuten_auth.login', '/login', factory=empty_resource_factory)
    config.add_route('rakuten_auth.verify', '/verify', factory=empty_resource_factory)
    config.add_route('rakuten_auth.verify2', '/verify2', factory=empty_resource_factory)
    config.add_route('rakuten_auth.error', '/error', factory=empty_resource_factory)
    config.add_route('cart.logout', '/logout')

    config.include(setup_nogizaka_auth)

class CartInterface(object):
    def get_cart(self, request, retrieve_invalidated=False):
        from .api import get_cart, get_cart_safe
        from .exceptions import NoCartError
        if retrieve_invalidated:
            return get_cart(request) # for_update=True
        else:
            try:
                return get_cart_safe(request) # for_update=True
            except NoCartError:
                return None

    def get_cart_by_order_no(self, request, order_no, retrieve_invalidated=False):
        from .api import get_cart_by_order_no, validate_cart
        cart = get_cart_by_order_no(request, order_no) # for_update=True
        if cart is not None:
            if not retrieve_invalidated and not validate_cart(request, cart):
                return None
        return cart

    def get_success_url(self, request):
        return request.route_url('payment.confirm')

    def make_order_from_cart(self, request, cart):
        from .api import make_order_from_cart
        return make_order_from_cart(request, cart)

    def cont_complete_view(self, context, request, order_no, magazine_ids):
        from .views import cont_complete_view
        return cont_complete_view(context, request, order_no, magazine_ids)

def setup_cart_interface(config):
    config.set_cart_interface(CartInterface())

def setup__renderers(config):
    config.include('pyramid_mako')
    config.add_mako_renderer('.html')
    config.add_mako_renderer('.txt')

def setup_static_views(config):
    settings = config.registry.settings
    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
        settings["s3.bucket_name"],
        exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
        mapping={
            FC_AUTH_STATIC_ASSET_SPEC: FC_AUTH_CDN_URL_PREFIX,
            CART_STATIC_ASSET_SPEC: CART_CDN_URL_PREFIX
            }
        ))
    config.add_static_view(CART_STATIC_URL_PREFIX, CART_STATIC_ASSET_SPEC, cache_max_age=3600)

def setup_mobile(config):
    config.include('altair.mobile')
    config.add_smartphone_support_predicate('altair.app.ticketing.cart.predicates.smartphone_enabled')

def setup_payment_delivery_plugins(config):
    config.include('altair.app.ticketing.checkout')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.sej')
    config.include('altair.app.ticketing.sej.userside_impl')
    config.include('altair.app.ticketing.qr')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')

def setup_cms_communication_api(config):
    ## cmsとの通信
    bind_communication_api(config,
                            "..api.impl.CMSCommunicationApi",
                            config.registry.settings["altair.cms.api_url"],
                            config.registry.settings["altair.cms.api_key"]
                            )

def setup_tweens(config):
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)
    config.add_tween('.tweens.OrganizationPathTween', over=EXCVIEW)
    config.add_tween('.tweens.response_time_tween_factory', over=MAIN)
    config.add_tween('.tweens.PaymentPluginErrorConverterTween', under=EXCVIEW)
    config.add_tween('.tweens.CacheControlTween')

def setup_layouts(config):
    config.include("pyramid_layout")
    from altair.pyramid_dynamic_renderer import RendererHelperProxy, RequestSwitchingRendererHelperFactory
    selectable_renderer_helper_factory = RequestSwitchingRendererHelperFactory(
        fallback_renderer='notfound.html',
        name_builder=lambda name, view_context, request: 'altair.app.ticketing.cart:templates/__layouts__/%(ua_type)s/%(path)s' % dict(ua_type=view_context.ua_type, path=name),
        view_context_factory=lambda name, package, registry, request, **kwargs: request.view_context
        )
    def layout_selector(name):
        return RendererHelperProxy(
            selectable_renderer_helper_factory,
            name
            )
    config.add_lbr_layout(".layouts.Layout", template=layout_selector("booster.html"), name='booster')
    config.add_lbr_layout(".layouts.Layout", template=layout_selector("fc.html"), name='fc')

def setup_panels(config):
    from .rendering import selectable_renderer
    config.add_panel(
        'altair.app.ticketing.cart.panels.input_form',
        'input_form',
        renderer=selectable_renderer('booster/_form.html')
        )
    config.add_panel(
        'altair.app.ticketing.cart.panels.complete_notice',
        'complete_notice',
        renderer=selectable_renderer('booster/_complete_notice.html')
        )
    config.add_panel(
        'altair.app.ticketing.cart.panels.input_form',
        'mobile_input_form',
        renderer=selectable_renderer('booster/_form.html')
        )
    config.add_panel(
        'altair.app.ticketing.cart.panels.complete_notice',
        'mobile_complete_notice',
        renderer=selectable_renderer('booster/_complete_notice.html')
        )

def setup_routes(config):
    # 規約
    config.add_route('cart.agreement', 'events/{event_id}/agreement', factory='.resources.compat_ticketing_cart_resource_factory')
    config.add_route('cart.agreement2', 'performances/{performance_id}/agreement', factory='.resources.PerformanceOrientedTicketingCartResource')

    config.add_route('cart.agreement.compat', 'events/agreement/{event_id}', factory='.resources.compat_ticketing_cart_resource_factory')
    config.add_route('cart.agreement2.compat', 'performances/agreement/{performance_id}', factory='.resources.PerformanceOrientedTicketingCartResource')

    # PC/Smartphone切替
    config.add_route('cart.switchpc', 'events/{event_id}/switchpc', factory='.resources.SwitchUAResource')
    config.add_route('cart.switchsp', 'events/{event_id}/switchsp', factory='.resources.SwitchUAResource')
    config.add_route('cart.switchpc.perf', 'performances/{performance_id}/switchpc', factory='.resources.SwitchUAResource')
    config.add_route('cart.switchsp.perf', 'performances/{performance_id}/switchsp', factory='.resources.SwitchUAResource')

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
    config.add_route('cart.venue_drawing', 'performances/{performance_id}/venues/{venue_id}/drawing/{part}')
    config.add_route('cart.products', 'events/{event_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products', factory='.resources.EventOrientedTicketingCartResource')
    config.add_route('cart.products2', 'performances/{performance_id}/sales_segment/{sales_segment_id}/seat_types/{seat_type_id}/products')

    # order / payment / release
    config.add_route('cart.order', 'order/sales/{sales_segment_id}', factory='.resources.SalesSegmentOrientedTicketingCartResource')
    config.add_route('cart.payment', 'payment/sales/{sales_segment_id}', factory='.resources.SalesSegmentOrientedTicketingCartResource')
    config.add_route('cart.point', 'rsp', factory='.resources.CartBoundTicketingCartResource')
    config.add_route('cart.extra_form', 'extra_form', factory='.resources.CartBoundTicketingCartResource')
    config.add_route('cart.release', 'release')

    # 完了／エラー
    config.add_route('payment.confirm', 'confirm', factory='.resources.CartBoundTicketingCartResource')
    config.add_route('payment.finish.mobile', 'completed', request_method='POST', factory='.resources.CartBoundTicketingCartResource')
    config.add_route('payment.finish', 'completed', factory='.resources.CompleteViewTicketingCartResource')

    config.add_route('cart.contact', 'contact')

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='.resources.PerformanceOrientedTicketingCartResource'
        )
    config.include('altair.app.ticketing.setup_beaker_cache')

    ### includes altair.*
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.mq')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.sqlahelper')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_boto.s3.assets')

    config.include('altair.app.ticketing.users')
    config.include('altair.app.ticketing.orders')
    config.include('altair.app.ticketing.organization_settings')
    config.include('altair.app.ticketing.venues.setup_components')

    config.include(setup_components)
    config.include(setup_temporary_store)
    config.include(setup_tweens)
    config.include(setup_auth)
    config.include(setup__renderers)
    config.include(setup_payment_delivery_plugins)
    config.include(setup_mobile)
    config.include(setup_cart_interface)
    config.include(setup_mq)
    config.include(setup_payment_renderers)
    config.include(setup_cms_communication_api)
    config.include(setup_static_views)
    config.include(setup_layouts)
    config.include(import_mail_module)
    config.include(setup_panels)
    config.include(setup_routes)

    config.include('.')
    config.include('.view_context')
    config.include('.errors')
    config.include('.preview')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    config.scan()

    app = config.make_wsgi_app()

    return direct_static_serving_filter_factory({
        CART_STATIC_URL_PREFIX: CART_STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
    })(global_config, app)

def includeme(config):
    config.include('.request')
