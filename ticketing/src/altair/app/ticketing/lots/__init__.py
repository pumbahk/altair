# -*- coding:utf-8 -*-

"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from pyramid.tweens import INGRESS
from pyramid_selectable_renderer import SelectableRendererSetup
from pyramid_selectable_renderer.custom import ReceiveTemplatePathFormat, ReceiveTemplatePathCandidatesDict, SelectByRequestGen
from altair.app.ticketing.core.api import get_organization

import sqlalchemy as sa
import sqlahelper

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        #return self.request.organization.setting.auth_type
        #return get_organization(self.request).setting.auth_type

        if hasattr(self.request.context, "lot"):
            return self.request.context.lot.auth_type

def register_globals(event):
    from . import helpers
    event.update(h=helpers)


@SelectByRequestGen.generate
def get_template_path_args(request):
    try:
        return dict(membership=get_organization(request).short_name)
    except:
        return dict(membership="__default__")

selectable_renderer = SelectableRendererSetup(
    ReceiveTemplatePathFormat,
    get_template_path_args,
    renderer_name="selectable_renderer"
    )

def includeme(config):
    config.include(setup_cart)
    config.include(setup_mailtraverser)
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    #config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    #config.add_renderer('json'  , 'altair.app.ticketing.renderers.json_renderer_factory')
    config.include('altair.app.ticketing.renderers')
    selectable_renderer.register_to(config)

    # static_viewにfactoryを適用したくないので、add_routeで個別指定する
    factory=".resources.lot_resource_factory"
    def add_route(*args, **kwargs):
        if 'factory' not in kwargs:
            kwargs['factory'] = factory
        config.add_route(*args, **kwargs)

    # 申し込みフェーズ
    add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    add_route('lots.entry.step1', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step1', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step2', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step2', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step3', 'events/{event_id}/entry/{lot_id}/step3', factory='.resources.LotOptionSelectionResource')
    add_route('lots.entry.step4', 'events/{event_id}/entry/{lot_id}/step4')
    add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')

    # 申し込み確認
    config.add_route('lots.review.index', 'review')

    # 当選フェーズ
    #config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    #config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    #config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')
  
    # 楽天認証コールバック
    add_route('rakuten_auth.login', '/login')
    add_route('rakuten_auth.verify', '/verify')
    add_route('rakuten_auth.verify2', '/verify2')
    add_route('rakuten_auth.error', '/error')

    config.scan(".")

# TODO: carts.includemeに移動
def setup_cart(config):

    from altair.app.ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from altair.app.ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

    from altair.app.ticketing.payments.interfaces import IGetCart
    cart_getter = config.maybe_dotted(".api.get_entry_cart")
    reg.registerUtility(cart_getter, IGetCart)


def setup_mailtraverser(config):
    from altair.app.ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

def main(global_config, **local_config):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = sa.engine_from_config(settings, poolclass=NullPool,
                                   isolation_level='READ COMMITTED',
                                   pool_recycle=60)

    sqlahelper.add_engine(engine)
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 

    config = Configurator(settings=settings,
                          session_factory=session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('c_static', 'altair.app.ticketing.cart:static', cache_max_age=3600)

    config.include(".")
    config.include(".sendmail")

    ### includes altair.*
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.exclog')

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={"altair.app.ticketing.cart:static/": "/cart/static/"}))

    config.include('altair.mobile')

    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.users')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)

    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_tz')

    config.set_authorization_policy(ACLAuthorizationPolicy())
    return config.make_wsgi_app()
