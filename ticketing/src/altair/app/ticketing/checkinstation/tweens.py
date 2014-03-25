# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from pyramid.settings import asbool
from pyramid.httpexceptions import HTTPBadRequest 
from altair.app.ticketing.login.main.utils import get_auth_identifier_from_client_certified_request

def client_certified_tween(handler, registry):
    ## todo: enable, disable
    if asbool(registry.settings.get("altair.checkinstation.enable.client_certificate", False)):
        logger.info("altair.checkinstation.enable.client_certificate is enabled.")
        def tween(request):
            auth_identifier = get_auth_identifier_from_client_certified_request(request)
            if auth_identifier is None:
                logger.warn("client certificate is not found")
                return HTTPBadRequest(u"E@:クライアント証明書が掲示されていません")
            return handler(request)
        return tween
    else:
        def disable_tween(request):
            return handler(request)
        return disable_tween

