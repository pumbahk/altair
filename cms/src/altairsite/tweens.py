# -*- coding:utf-8 -*-
import re
import logging
from zope.interface import directlyProvides
from pyramid.response import Response
from pyramid.renderers import render
from altair.exclog.api import build_exception_message, log_exception_message

logger = logging.getLogger(__name__)
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.mobile.tweens import make_mobile_response
from altair.mobile.tweens import convert_response_if_necessary
from altair.mobile.tweens import mobile_request_factory
from altair.mobile.api import detect
from . import PC_ACCESS_COOKIE_NAME
__all__ = ["IMobileRequest", 
           "ISmartphoneRequest", 
           "mobile_encoding_convert_factory", 
           "mobile_request_factory", 
           "smartphone_request_factory"]

SMARTPHONE_USER_AGENT_RX = re.compile("iPhone|iPod|Opera Mini|Android.*Mobile|NetFront|PSP|BlackBerry")

def smartphone_request_factory(handler, registry):
    def tween(request):
        if not PC_ACCESS_COOKIE_NAME in request.cookies:
            directlyProvides(request, ISmartphoneRequest)
        return handler(request)
    return tween

def attach_smartphone_request(request):
    ## for smartphone
    if "HTTP_USER_AGENT" in request.environ and not PC_ACCESS_COOKIE_NAME in request.cookies:
        uagent = request.environ["HTTP_USER_AGENT"]
        if SMARTPHONE_USER_AGENT_RX.search(uagent):
            directlyProvides(request, ISmartphoneRequest)

def mobile_encoding_convert_factory(handler, registry):
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
                logger.warning(str(e))
                exception_message = build_exception_message(request)
                if exception_message:
                    log_exception_message(request, *exception_message)
                # XXX: テンプレ大丈夫?
                return convert_response_if_necessary(request, Response(status=400, body=render("altaircms:templates/mobile/default_notfound.html", dict(), request)))
        else:
            attach_smartphone_request(request)
            request.is_mobile = False
            return handler(request)
    return tween

