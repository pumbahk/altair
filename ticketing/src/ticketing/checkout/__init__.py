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

    checkout_api = api.CheckoutAPI(service_id, success_url, fail_url, auth_method, is_test)
    config.registry.utilities.register([], interfaces.ICheckoutAPI, "", checkout_api)

    """
    楽天あんしん決済 メッセージ署名設定
    """
    secret = config.registry.settings.get('altair_checkout.secret')

    if auth_method == "HMAC-SHA1":
        hmac_sha1_signer = api.HMAC_SHA1(secret)
        config.registry.utilities.register([], interfaces.ISigner, "HMAC", hmac_sha1_signer)
    elif auth_method == "HMAC-MD5":
        hmac_md5_signer = api.HMAC_MD5(secret)
        config.registry.utilities.register([], interfaces.ISigner, "HMAC", hmac_md5_signer)
