# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid_beaker import session_factory_from_settings

import logging

logger = logging.getLogger(__name__)

def includeme(config):
    # ディレクティブ
    config.add_directive("add_payment_method", ".directives.add_payment_method")
    # 購入系
    config.add_route('cart.index', 'events/{event_id}')
    config.add_route('cart.seat_types', 'events/{event_id}/performances/{performance_id}/seat_types')
    config.add_route('cart.products', 'events/{event_id}/performances/{performance_id}/seat_types/{seat_type_id}/products')

    config.add_route('cart.order', 'order')
    config.add_route('cart.payment', 'payment')

    # 決済系(マルチ決済)
    config.add_route("payment.secure3d", 'payment/3d')
    config.add_route("cart.secure3d_result", 'payment/3d/result')

    # 決済系(あんしん決済)
    config.add_route("payment.checkout", 'payment/checkout')

    # 決済系(セブンイレブン)
    config.add_route("payment.sej", 'payment/sej')
    # 完了／エラー
    config.add_route('payment.finish', 'completed')

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

    # 決済方法登録
    # セブンイレブン
    # 安心決済
    # クレジットカード／マルチ決済
    config.add_payment_method('1', 'payment.sej')
    config.add_payment_method('2', 'payment.checkout')
    config.add_payment_method('3', 'payment.secure3d')

    # 楽天認証URL
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')


def main(global_config, **settings):
    engine = engine_from_config(settings)
    my_session_factory = session_factory_from_settings(settings)
    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, session_factory=my_session_factory)
    config.set_root_factory('.resources.TicketingCartResrouce')
    config.registry['sa.engine'] = engine
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
    config.add_static_view('img', 'ticketing.cart:static', cache_max_age=3600)

    config.include('.')
    config.include('.rakuten_auth')
    config.include('.plugins.multicheckout')
    config.scan()
    config.include('..checkout')
    config.include('..multicheckout')
    config.scan('..orders.models')

    return config.make_wsgi_app()
