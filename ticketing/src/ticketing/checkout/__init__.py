# -*- coding:utf-8 -*-

from .interfaces import ISigner
from . import api

def includeme(config):
    """ 
    あんしん決済 サービスID
    あんしん決済 アクセスキー 
    あんしん決済 Success URL
    あんしん決済 Fail URL 
    """
    utilities = config.registry.utilities

    secret = config.registry.settings.get('altair_checkout.secret')
    authmethod = config.registry.settings.get('altair_checkout.authmethod')

    hmac_sha1_signer = api.HMAC_SHA1(secret)
    hmac_md5_signer = api.HMAC_MD5(secret)
    utilities.register([], ISigner, "HMAC-SHA1", hmac_sha1_signer)
    utilities.register([], ISigner, "HMAC-MD5", hmac_md5_signer)

    if authmethod == "HMAC-SHA1":
        utilities.register([], ISigner, "", hmac_sha1_signer)
    elif authmethod == "HMAC-MD5":
        utilities.register([], ISigner, "", hmac_md5_signer)
