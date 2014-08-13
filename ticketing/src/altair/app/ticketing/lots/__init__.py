# -*- coding:utf-8 -*-

"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from pyramid.tweens import INGRESS
from pyramid_selectable_renderer import SelectableRendererSetup
from pyramid_selectable_renderer.custom import ReceiveTemplatePathFormat, ReceiveTemplatePathCandidatesDict, SelectByRequestGen
from altair.app.ticketing.wsgi import direct_static_serving_filter_factory

import sqlalchemy as sa
import sqlahelper


class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        if hasattr(self.request, "context") and hasattr(self.request.context, "lot"):
            return self.request.context.auth_type

def register_globals(event):
    from . import helpers
    event.update(h=helpers)


@SelectByRequestGen.generate
def get_template_path_args(request):
    # move to here because of circular dependency between modules.
    from altair.app.ticketing.cart import api as cart_api
    try:
        return dict(membership=cart_api.get_organization(request).short_name)
    except:
        return dict(membership="__default__")

selectable_renderer = SelectableRendererSetup(
    ReceiveTemplatePathFormat,
    get_template_path_args,
    renderer_name="selectable_renderer"
    )

def includeme(config):
    config.include('altair.app.ticketing.mails')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include(setup_cart)
    config.include(setup_mailtraverser)
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    #config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    #config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.include('altair.app.ticketing.renderers')
    selectable_renderer.register_to(config)
    config.include(setup_renderers)
    config.include('altair.app.ticketing.project_specific.nogizaka46.auth')

    # static_viewにfactoryを適用したくないので、add_routeで個別指定する
    factory=".resources.lot_resource_factory"
    def add_route(*args, **kwargs):
        if 'factory' not in kwargs:
            kwargs['factory'] = factory
        config.add_route(*args, **kwargs)

    # 申し込みフェーズ
    add_route('lots.entry.agreement', 'events/{event_id}/entry/{lot_id}/agreement')
    add_route('lots.entry.agreement.compat', 'events/agreement/{event_id}/entry/{lot_id}')
    add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    add_route('lots.entry.step1', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step1', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step2', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step2', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step3', 'events/{event_id}/entry/{lot_id}/step3', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step4', 'events/{event_id}/entry/{lot_id}/step4')
    add_route('lots.entry.sp_step1', 'events/{event_id}/entry/{lot_id}/sp_step1')
    add_route('lots.entry.sp_step2', 'events/{event_id}/entry/{lot_id}/sp_step2')
    add_route('lots.entry.sp_step3', 'events/{event_id}/entry/{lot_id}/sp_step3')
    add_route('lots.entry.sp_step4', 'events/{event_id}/entry/{lot_id}/sp_step4')
    add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')

    config.add_route('lots.review.index', 'review')

    config.add_nogizaka_entrypoint('lots.entry.agreement')
    config.add_nogizaka_entrypoint('lots.entry.agreement.compat')
    config.add_nogizaka_entrypoint('lots.entry.index')

    # 当選フェーズ
    #config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    #config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    #config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')
  
    # 楽天認証コールバック
    add_route('rakuten_auth.login', '/login')
    add_route('rakuten_auth.verify', '/verify')
    add_route('rakuten_auth.verify2', '/verify2')
    add_route('rakuten_auth.error', '/error')

    config.scan(".subscribers")
    config.scan(".views")
    config.scan(".mobile_views")
    config.scan(".smartphone_views")
    config.scan(".layouts")


class CartInterface(object):
    def get_cart(self, request):
        from .api import get_entry_cart
        return get_entry_cart(request)

    def get_success_url(self, request):
        from .urls import entry_confirm
        cart = self.get_cart(request)
        request.matchdict['lot_id'] = cart.lot.id
        request.matchdict['event_id'] = cart.sales_segment.event.id
        return entry_confirm(request)


def setup_cart(config):
    from altair.app.ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from altair.app.ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

    config.set_cart_interface(CartInterface()) 


def setup_renderers(config):
    import os
    import functools
    from zope.interface import implementer
    from pyramid.interfaces import IRendererFactory
    from pyramid.renderers import RendererHelper
    from pyramid.path import AssetResolver
    from pyramid_selectable_renderer import SelectableRendererFactory
    from altair.app.ticketing.payments.interfaces import IPaymentViewRendererLookup

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

    renderer_factory = functools.partial(
        SelectableRendererFactory,
        selectable_renderer.select_fn
        ) # XXX

    config.add_payment_view_renderer_lookup(
        SelectByOrganization(
            renderer_factory,
            selectable_renderer
            ),
        'select_by_organization'
        )
    config.add_payment_view_renderer_lookup(
        Overridable(
            renderer_factory,
            selectable_renderer,
            AssetResolver(__name__)
            ),
        'overridable'
        )


def setup_mailtraverser(config):
    from altair.app.ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

STATIC_URL_PREFIX = '/static/'
STATIC_URL_S3_PREFIX = '/lots/static/'
STATIC_ASSET_SPEC = 'altair.app.ticketing.lots:static/'
CART_STATIC_URL_PREFIX = '/c_static/'
CART_STATIC_S3_URL_PREFIX = '/cart/static/'
CART_STATIC_ASSET_SPEC = 'altair.app.ticketing.cart:static/'
FC_AUTH_URL_PREFIX = '/fc_auth/static/'
FC_AUTH_STATIC_ASSET_SPEC = "altair.app.ticketing.fc_auth:static/"

def main(global_config, **local_config):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = sa.engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')

    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings)

    config.include('altair.app.ticketing.setup_beaker_cache')

    ### includes altair.*
    config.include('altair.httpsession.pyramid')
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')
    config.include('altair.exclog')
    config.include('altair.rakuten_auth')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_tz')
    config.include('altair.mobile')
    config.add_smartphone_support_predicate('altair.app.ticketing.cart.predicates.smartphone_enabled')

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={
                FC_AUTH_STATIC_ASSET_SPEC: FC_AUTH_URL_PREFIX,
                CART_STATIC_ASSET_SPEC: CART_STATIC_S3_URL_PREFIX,
                }))
    config.add_static_view(STATIC_URL_PREFIX, STATIC_ASSET_SPEC, cache_max_age=3600)
    config.add_static_view(CART_STATIC_URL_PREFIX, CART_STATIC_ASSET_SPEC, cache_max_age=3600)

    config.include(".")
    config.include(".sendmail")

    config.include('altair.app.ticketing.fc_auth')
    config.include('altair.app.ticketing.users')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.sej')
    config.include('altair.app.ticketing.sej.userside_impl')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)

    ### whattime preview
    config.include("altair.app.ticketing.cart.preview")

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_who_api_decider('altair.app.ticketing.lots:WhoDecider')
    from altair.auth import set_auth_policy
    set_auth_policy(config, 'altair.app.ticketing.security:auth_model_callback')

    app = config.make_wsgi_app()

    return direct_static_serving_filter_factory({
        STATIC_URL_PREFIX: STATIC_ASSET_SPEC,
        CART_STATIC_URL_PREFIX: CART_STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
    })(global_config, app)
