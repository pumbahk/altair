# -*- coding:utf-8 -*-
import re
import logging
from zope.interface import directlyProvides
from .interfaces import IMobileRequest, ISmartphoneRequest
from pyramid.threadlocal import manager
from pyramid.response import Response
from .api import detect
logger = logging.getLogger(__name__)


def _convert_response_for_docomo(response):
    if response.content_type is not None and response.content_type.startswith('text/html'):
        response.content_type = 'application/xhtml+xml'
    return response

def _convert_response_sjis(response):
    encoding = 'Shift_JIS'
    if response.content_type is not None and response.content_type.startswith("text"):
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

def make_mobile_request(request):
    session = getattr(request, 'session', None)
    decoded = request.decode("cp932")
    request.environ.update(decoded.environ)
    decoded.environ = request.environ
    decoded.session = session
    manager.get()['request'] = decoded # hack!
    decoded.is_mobile = True
    directlyProvides(decoded, IMobileRequest)
    decoded.registry = request.registry
    decoded.mobile_ua = request.mobile_ua

    ## todo:remove.
    decoded.is_docomo = request.mobile_ua.carrier.is_docomo #cms, usersite compatibility
    return decoded

def make_mobile_response(handler, request):
    decoded = make_mobile_request(request)
    response = handler(decoded)
    response = _convert_response_sjis(response)
    if request.mobile_ua.carrier.is_docomo:
        response = _convert_response_for_docomo(response)
    return response


def attach_smartphone_request_if_necessary(request):
    if "HTTP_USER_AGENT" in request.environ:
        if SMARTPHONE_USER_AGENT_RX.match(request.environ["HTTP_USER_AGENT"]):
            directlyProvides(request, ISmartphoneRequest)
    return request

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
    
def mobile_encoding_convert_factory(handler, registry, on_decode_error=_on_error_return_error_response):
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
            # attach_smartphone_request_if_necessary(request)
            return handler(request)
    return tween
