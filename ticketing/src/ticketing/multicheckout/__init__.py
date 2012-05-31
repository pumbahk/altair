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
    shop_id = config.registry.settings.get('altair_checkout3d.shop_id')
    auth_id = config.registry.settings.get('altair_checkout3d.auth_id')
    password = config.registry.settings.get('altair_checkout3d.auth_password')
    Checkout3D = config.maybe_dotted(__name__ + '.api.Checkout3D')
    checkout3d = Checkout3D(auth_id, password, shop_code=shop_id, api_base_url=base_url)

    reg = config.registry

    reg.utilities.register([], interfaces.IMultiCheckout, "", checkout3d)

def main(global_conf, **settings):
    from pyramid.config import Configurator
    config = Configurator(settings=settings)
    config.include(".")
    config.include(".demo")
    return config.make_wsgi_app()