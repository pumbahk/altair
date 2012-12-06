# -*- coding:utf-8 -*-

"""
"""
from pyramid.config import Configurator
from pyramid.interfaces import IRequest
from pyramid.session import UnencryptedCookieSessionFactoryConfig
import sqlalchemy as sa
import sqlahelper

def register_globals(event):
    from . import helpers
    event.update(h=helpers)

def includeme(config):
    config.include(setup_cart)
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')

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
  
    config.scan(".")

# TODO: carts.includemeに移動
def setup_cart(config):

    from ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

def main(global_conf, **settings):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    engine = sa.engine_from_config(settings)
    sqlahelper.add_engine(engine)
    config = Configurator(settings=settings)
    session_factory = UnencryptedCookieSessionFactoryConfig("secret")
    config.set_session_factory(session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include(".")
    config.include(".secure")
    config.include("ticketing.payments")
    config.include("ticketing.cart.plugins")

    return config.make_wsgi_app()
