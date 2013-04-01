# -*- coding:utf-8 -*-

"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid_beaker import session_factory_from_settings
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from ticketing.core.api import get_organization

import sqlalchemy as sa
import sqlahelper

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        #return self.request.organization.setting.auth_type
        return get_organization(self.request).setting.auth_type

def register_globals(event):
    from . import helpers
    event.update(h=helpers)


def selectable_renderer(config):
    config.include("ticketing.cart.selectable_renderer")
    domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
    config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)
    selector = config.maybe_dotted("ticketing.cart.selectable_renderer.ByDomainMappingSelector")(domain_candidates)
    config.add_selectable_renderer_selector(selector)

def includeme(config):
    config.include(setup_cart)
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    selectable_renderer(config)

    # 申し込みフェーズ
    config.add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    config.add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    config.add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')

    # 申し込み確認
    config.add_route('lots.review.index', 'review')

    # 当選フェーズ
    config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')
  
    # 楽天認証コールバック
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')

    config.scan(".")

# TODO: carts.includemeに移動
def setup_cart(config):

    from ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

def main(global_config, **local_config):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(settings)
    sqlahelper.add_engine(engine)
    config = Configurator(settings=settings)
    session_factory = session_factory_from_settings(settings)

    config.set_session_factory(session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('c_static', 'ticketing.cart:static', cache_max_age=3600)

    config.include(".")
    config.include(".secure")

    ### includes altair.*
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.exclog')


    config.include('ticketing.rakuten_auth')
    config.include("ticketing.payments")
    config.include("ticketing.payments.plugins")
    config.add_tween('ticketing.tweens.session_cleaner_factory', over=EXCVIEW)

    config.set_authorization_policy(ACLAuthorizationPolicy())
    return config.make_wsgi_app()
