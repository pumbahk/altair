# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

from . import interfaces
import logging


logger = logging.getLogger(__name__)

def includeme(config):
    """ 設定値取得など

    設定項目

    - altair_checkout3d.base_url = https://payment.rakuten-card.co.jp:9480/gh-ws/1.0/storecd/
    - altair_checkout3d.shop_id 店舗ID
    - altair_checkout3d.auth_id API BASIC認証ユーザーID
    - altair_checkout3d.auth_password API BASIC認証パスワード

    """

    base_url = config.registry.settings.get('altair_checkout3d.base_url')
    multicheckouts = {}
    for k, v in config.registry.settings.items():
        parts = k.split(".")
        if len(parts) != 3:
            continue

        if parts[0] != 'altair_checkout3d':
            continue

        shop_name = parts[1]
        shop_data = multicheckouts.get(shop_name, {})
        shop_data[parts[2]] = v
        multicheckouts[shop_name] = shop_data
        
    #shop_id = config.registry.settings.get('altair_checkout3d.shop_id')
    #auth_id = config.registry.settings.get('altair_checkout3d.auth_id')
    #password = config.registry.settings.get('altair_checkout3d.auth_password')

    reg = config.registry
    Checkout3D = config.maybe_dotted(__name__ + '.api.Checkout3D')
    for k, v in multicheckouts.items():
        shop_name = k
        logger.info('setup multicheckout for %s' % shop_name)
        shop_id = v['shop_id']
        auth_id = v['auth_id']
        password = v['auth_password']
        checkout3d = Checkout3D(auth_id, password, shop_code=shop_id, api_base_url=base_url)

        reg.utilities.register([], interfaces.IMultiCheckout, shop_name, checkout3d)

def main(global_conf, **settings):
    from pyramid.config import Configurator
    from pyramid.session import UnencryptedCookieSessionFactoryConfig
    my_session_factory = UnencryptedCookieSessionFactoryConfig("itsaseekreet")
    config = Configurator(
        settings=settings,
        session_factory=my_session_factory)
    config.include(".")
    config.include(".demo")
    return config.make_wsgi_app()
