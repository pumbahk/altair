# -*- coding:utf-8 -*-

from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid_beaker import session_factory_from_settings

import logging

logger = logging.getLogger(__name__)

from ..api.impl import bound_communication_api ## cmsとの通信

def includeme(config):
    # ディレクティブ
    config.add_directive("add_payment_method", ".directives.add_payment_method")
    # 購入系
    config.add_route('cart.index', 'events/{event_id}')
    config.add_route('cart.seat_types', 'events/{event_id}/performances/{performance_id}/seat_types')
    config.add_route('cart.products', 'events/{event_id}/performances/{performance_id}/seat_types/{seat_type_id}/products')
    config.add_route('cart.date.products', 'events/{event_id}/products')

    config.add_route('cart.order', 'order')
    config.add_route('cart.payment', 'payment')

    # 決済系(マルチ決済)
    config.add_route("payment.secure3d", 'payment/3d')
    config.add_route("cart.secure3d_result", 'payment/3d/result')

    # 決済系(あんしん決済)
    config.add_route("payment.checkout", 'payment/checkout')
    config.add_route("payment.checkout_test", 'payment/checkout_test')

    # 決済系(セブンイレブン)
    config.add_route("payment.sej", 'payment/sej')

    # 完了／エラー
    config.add_route('payment.confirm', 'confirm')
    config.add_route('payment.finish', 'completed')


    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')

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

    config.add_subscriber('.mail.on_order_completed', '.events.OrderCompleted')

    config.include('.')
    config.include('.rakuten_auth')
    config.scan()
    config.include('..checkout')
    config.include('..multicheckout')
    config.scan('..orders.models')
    config.include('.plugins')

    ## cmsとの通信
    bound_communication_api(config, 
                            "..api.impl.CMSCommunicationApi", 
                            config.registry.settings["altaircms.event.notification_url"], 
                            config.registry.settings["altaircms.apikey"]
                            )
    return config.make_wsgi_app()
