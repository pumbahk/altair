# -*- encoding:utf-8 -*-
import uamobile

def _convert_response_for_mobile(response):
    encoding = 'Shift_JIS'
    if response.content_type.startswith("text"):
        response.body = response.unicode_body.encode("cp932", "replace")
        response.content_type = 'application/xhtml+xml; charset=%s' % encoding
    return response

"""
emoziを使い始めたらemojiのmappingテーブルも必要(from django-bpmobile)
"""


def mobile_encoding_convert_factory(handler, registry):
    def tween(request):
        request._ua = uamobile.detect(request.environ)
        if not request._ua.is_nonmobile():
            ## DeprecationWarning: Use req = req.decode('cp932')
            decoded = request.decode("cp932")
            decoded.registry = request.registry
            decoded._ua = request._ua
            response = handler(decoded)
            return _convert_response_for_mobile(response)
        else:
            return handler(request)
    return tween
