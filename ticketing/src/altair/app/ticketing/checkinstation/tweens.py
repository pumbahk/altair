# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPBadRequest 
from altair.app.ticketing.login.main.utils import get_auth_identifier_from_client_certified_request

def client_certified_tween(handler, registry):
    ## todo: enable, disable
    expected_identifier = registry.settings.get("altair.checkinstation.client.certificate.identifier", None)
    if expected_identifier:
        logger.info("altair.checkinstation.client.certificate.identifier found. using client certificate.")
        def tween(request):
            auth_identifier = get_auth_identifier_from_client_certified_request(request)
            if auth_identifier is None:
                logger.warn("client certificate is not found")
                return HTTPBadRequest(u"E@:クライアント証明書が掲示されていません")
            elif auth_identifier.startswith(expected_identifier):
                return handler(request)
            else:
                logger.info("certificate fail expected = actual : %s = %s", expected_identifier, auth_identifier)
                return HTTPBadRequest(u"E@:クライアント証明書が不正です")
        return tween
    else:
        def disable_tween(request):
            return handler(request)
        return disable_tween

