import uamobile
import logging
from zope.interface import directlyProvides
from ticketing.cart.interfaces import IMobileRequest
logger = logging.getLogger(__name__)

def _convert_response_for_mobile(response):
    encoding = 'Shift_JIS'
    if response.content_type.startswith("text"):
        response.body = response.unicode_body.encode("cp932", "replace")
        response.content_type = 'application/xhtml+xml; charset=%s' % encoding
    return response

def mobile_request_factory(handler, registry):
    def tween(request):
        directlyProvides(request, IMobileRequest)
        return handler(request)
    return tween
    
def mobile_encoding_convert_factory(handler, registry):
    def tween(request):
        request._ua = uamobile.detect(request.environ)
        if not request._ua.is_nonmobile():
            ## DeprecationWarning: Use req = req.decode('cp932')
            decoded = request.decode("cp932")
            decoded.registry = request.registry
            decoded._ua = request._ua
            logger.debug("**this is mobile access**")
            decoded.is_mobile = True
            directlyProvides(decoded, IMobileRequest)
            response = handler(decoded)
            return _convert_response_for_mobile(response)
        else:
            request.is_mobile = False
            logger.debug("**this is pc access**")
            return handler(request)
    return tween
