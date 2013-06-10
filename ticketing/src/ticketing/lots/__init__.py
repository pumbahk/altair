# -*- coding:utf-8 -*-

"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid_beaker import (
    session_factory_from_settings,
    set_cache_regions_from_settings,
    )
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from pyramid.tweens import INGRESS

import sqlalchemy as sa
import sqlahelper

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        #return self.request.organization.setting.auth_type
        return self.request.organization.setting.auth_type

def register_globals(event):
    from . import helpers
    event.update(h=helpers)


def add_routes(config):
    # 申し込みフェーズ
    config.add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    config.add_route('lots.entry.step1', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step1', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step2', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step2', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step3', 'events/{event_id}/entry/{lot_id}/step3', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step4', 'events/{event_id}/entry/{lot_id}/step4')
    config.add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    config.add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')

    # 申し込み確認
    config.add_route('lots.review.index', 'review')

    # 当選フェーズ
    #config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    #config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    #config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')
  
def includeme(config):
    raise NotImplementedError()

def setup_cart(config):
    from ticketing.payments.interfaces import IGetCart
    cart_getter = config.maybe_dotted(".api.get_entry_cart")
    config.registry.registerUtility(cart_getter, IGetCart)

def setup_mailtraverser(config):
    from ticketing.mails.traverser import EmailInfoTraverser
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
    session_factory = session_factory_from_settings(settings)
    set_cache_regions_from_settings(settings) 
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings,
                          root_factory=".resources.lot_resource_factory",
                          session_factory=session_factory)

    from ticketing import setup_standard_renderers
    config.include(setup_standard_renderers)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('c_static', 'ticketing.cart:static', cache_max_age=3600)

    ### includes altair.*
    config.include("altair.cdnpath")
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.mobile')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_tz')
    config.include('altair.rakuten_auth')

    ## includes ticketing.*
    config.include('ticketing.cart')
    config.include('ticketing.users')
    config.include("ticketing.multicheckout")
    config.include("ticketing.payments")
    config.include("ticketing.payments.plugins")
    config.include("ticketing.cart.selectable_renderer")

    ## includes .
    config.include(".sendmail")

    ## routes and views
    config.include(setup_cart)
    config.include(setup_mailtraverser)
    config.include(add_routes)
    from ticketing.cart import add_rakuten_auth_routes
    config.include(add_rakuten_auth_routes)
    config.scan(".")

    ## tweens
    config.add_tween('ticketing.cart.tweens.altair_host_tween_factory',
        under='altair.mobile.tweens.mobile_encoding_convert_factory',
        over='altair.auth.activate_who_api_tween')
    config.add_tween('ticketing.tweens.session_cleaner_factory', under=INGRESS)

    ## events
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')

    ## auth
    config.set_authorization_policy(ACLAuthorizationPolicy())

    ## cdnpath
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"], 
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")), 
            mapping={"ticketing.cart:static/": "/cart/static/"}))

    return config.make_wsgi_app()
