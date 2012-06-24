# -*- coding:utf-8 -*-

from . import interfaces
from . import api

def includeme(config):

    """
    楽天あんしん決済 API設定
    """
    service_id = config.registry.settings.get('altair_checkout.service_id')
    success_url = config.registry.settings.get('altair_checkout.success_url')
    fail_url = config.registry.settings.get('altair_checkout.fail_url')
    auth_method = config.registry.settings.get('altair_checkout.auth_method')
    is_test = config.registry.settings.get('altair_checkout.is_test', False)

    checkout_api = api.Checkout(service_id, success_url, fail_url, auth_method, is_test)
    config.registry.utilities.register([], interfaces.ICheckout, "", checkout_api)

    """
    楽天あんしん決済 メッセージ署名設定
    """
    secret = config.registry.settings.get('altair_checkout.secret')

    if auth_method == "HMAC-SHA1":
        config.registry.utilities.register([], interfaces.ISigner, "HMAC", api.HMAC_SHA1(secret))
    elif auth_method == "HMAC-MD5":
        config.registry.utilities.register([], interfaces.ISigner, "HMAC", api.HMAC_MD5(secret))
