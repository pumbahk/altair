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
