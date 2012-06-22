# -*- encoding:utf-8 -*-
import uamobile
from .response import convert_response_for_mobile

import urllib
def _convert(qstring):
    s = urllib.unquote(qstring)
    encoded = s.decode("cp932").encode("utf-8")
    return encoded
    return urllib.quote(encoded)

def mobile_encoding_convert_factory(handler, registry):
    def tween(request):
        request._ua = uamobile.detect(request.environ)
        if not request._ua.is_nonmobile():
            # request.environ['QUERY_STRING'] = _convert(request.environ["QUERY_STRING"])
            request.charset = "cp932"
            response = handler(request)
            return convert_response_for_mobile(response)
        else:
            return handler(request)
    return tween
