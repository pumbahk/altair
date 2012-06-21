# -*- encoding:utf-8 -*-
import uamobile
from .response import convert_response_for_mobile

def mobile_encoding_convert_factory(handler, registry):
    def tween(request):
        request._ua = uamobile.detect(request.environ)
        response = handler(request)
        if not request._ua.is_nonmobile():
            return convert_response_for_mobile(response)
        return response
    return tween
