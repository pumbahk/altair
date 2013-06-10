# -*- coding:utf-8 -*-
import logging
import functools
from pyramid.response import Response
from pyramid.renderers import render
from altair.exclog.api import build_exception_message, log_exception_message

logger = logging.getLogger(__name__)
from altair.mobile.interfaces import IMobileRequest, ISmartphoneRequest
from altair.mobile.tweens import convert_response_if_necessary
from altair.mobile.tweens import mobile_request_factory
from altair.mobile.tweens import mobile_encoding_convert_factory as convert_factory_original
from altair.mobile.tweens import smartphone_request_factory

__all__ = ["IMobileRequest",
           "ISmartphoneRequest", 
           "smartphone_request_factory", 
           "mobile_encoding_convert_factory", 
           "mobile_request_factory", 
           "smartphone_request_factory"]

def on_error_return_converted_response(e, request):
    logger.warning(str(e))
    exception_message = build_exception_message(request)
    if exception_message:
        log_exception_message(request, *exception_message)
    # XXX: テンプレ大丈夫?
    return convert_response_if_necessary(request, Response(status=400, body=render("altaircms:templates/mobile/default_notfound.html", dict(), request)))

mobile_encoding_convert_factory = functools.partial(convert_factory_original, 
                                                    on_decode_error=on_error_return_converted_response)
