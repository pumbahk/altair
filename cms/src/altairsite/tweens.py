# -*- coding:utf-8 -*-
import logging
from pyramid.response import Response
from pyramid.renderers import render
from altair.mobile.api import get_middleware

logger = logging.getLogger(__name__)

__all__ = [
    "on_error_return_converted_response",
    ]

def on_error_return_converted_response(e, request):
    middleware = get_middleware(request)
    return middleware._convert_response(
        request.mobile_ua,
        request,
        Response(
            status=400,
            body=render(
                # XXX: テンプレ大丈夫?
                "altaircms:templates/mobile/default_notfound.html",
                dict(),
                request
                )
            )
        )
