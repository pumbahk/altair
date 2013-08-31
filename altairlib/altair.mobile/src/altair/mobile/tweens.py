# -*- coding:utf-8 -*-
import re
import logging
from zope.interface import directlyProvides
from .interfaces import IMobileRequest, ISmartphoneRequest
from pyramid.response import Response
from pyramid.settings import asbool
from .api import detect, make_mobile_request
logger = logging.getLogger(__name__)
from . import PC_ACCESS_COOKIE_NAME

def _convert_response_for_docomo(response):
    if response.content_type is not None and response.content_type.startswith('text/html'):
        response.content_type = 'application/xhtml+xml'
    return response

def _convert_response_sjis(response):
    encoding = 'Shift_JIS'
    if response.content_type is not None and response.content_type.startswith("text") and response.charset is not None:
        response.body = response.unicode_body.encode("cp932", "replace")
        response.charset = encoding
    return response

def convert_response_if_necessary(request, response):
    response = _convert_response_sjis(response)
    if request.mobile_ua.carrier.is_docomo:
        response = _convert_response_for_docomo(response)
    return response

def mobile_request_factory(handler, registry):
    """all requests are treated as mobile request"""
    def tween(request):
        request.mobile_ua = detect(request)
        return make_mobile_response(handler, request)
    return tween

def make_mobile_response(handler, request):
    decoded = make_mobile_request(request)
    response = handler(decoded)
    response = _convert_response_sjis(response)
    if request.mobile_ua.carrier.is_docomo:
        response = _convert_response_for_docomo(response)
    return response


def attach_smartphone_request_if_necessary(request):
    ## for smartphone
    if "HTTP_USER_AGENT" in request.environ and not PC_ACCESS_COOKIE_NAME in request.cookies:
        uagent = request.environ["HTTP_USER_AGENT"]
        if SMARTPHONE_USER_AGENT_RX.search(uagent):
            directlyProvides(request, ISmartphoneRequest)

## for smartphone
SMARTPHONE_USER_AGENT_RX = re.compile("iPhone|iPod|Opera Mini|Android.*Mobile|NetFront|PSP|BlackBerry")

def smartphone_request_factory(handler, registry):
    def tween(request):
        directlyProvides(request, ISmartphoneRequest)
        return handler(request)
    return tween

def _on_error_return_error_response(e, request):
    logger.warning(str(e))
    return Response(status=400, body=str(e))

def _attach_for_smartphone(registry):
    is_smartphone_enable = registry.settings.get("altair.mobile.enable.smartphone")
    if is_smartphone_enable is None:
        logger.warn("settings: altair.mobile.enable.smartphone not found. disabled.")
    is_smartphone_enable = asbool(is_smartphone_enable)
    if is_smartphone_enable:
        return attach_smartphone_request_if_necessary
    else:
        logger.info("settings: smartphone support is disabled")
        return lambda x : x

def mobile_encoding_convert_factory(handler, registry, on_decode_error=_on_error_return_error_response):
    attach_for_smartphone = _attach_for_smartphone(registry)
    def tween(request):
        if not hasattr(request, "mobile_ua"):
            request.mobile_ua = detect(request)
        if IMobileRequest.providedBy(request):
            return handler(request)
        if not request.mobile_ua.carrier.is_nonmobile:
            ## DeprecationWarning: Use req = req.decode('cp932')
            try:
                return make_mobile_response(handler, request)
            except UnicodeDecodeError as e:
                return on_decode_error(e, request)
        else:
            request.is_mobile = False
            attach_for_smartphone(request)
            return handler(request)
    return tween
