# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""

from . import api
from . import interfaces

def includeme(config):
    """ 設定値取得など
    """

    base_url = "https://payment.rakuten-card.co.jp:9480/gh-ws/1.0/storecd/"
    base_url = config.registry.settings.get('altair_checkout3d.base_url', base_url)
    shop_id = config.registry.settings.get('altair_checkout3d.shop_id')
    api_url = base_url % {'shop_id': shop_id}
    auth_id = config.registry.settings.get('altair_checkout3d.auth_id')
    password = config.registry.settings.get('altair_checkout3d.auth_password')
    checkout3d = api.Checkout3D(auth_id, password, shop_code=shop_id, api_base_url=api_url)

    reg = config.registry

    reg.utilities.register([], interfaces.IMultiCheckout, "", checkout3d)
