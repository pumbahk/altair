import uamobile
import logging
from zope.interface import directlyProvides
from ticketing.cart.interfaces import IMobileRequest
from pyramid.threadlocal import manager
logger = logging.getLogger(__name__)

def _convert_response_for_docomo(response):
    if response.content_type.startswith('text/html'):
        response.content_type = 'application/xhtml+xml'
    return response

def _convert_response_sjis(response):
    encoding = 'Shift_JIS'
    if response.content_type.startswith("text"):
        response.body = response.unicode_body.encode("cp932", "replace")
        response.charset = encoding
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
            session = getattr(request, 'session', None)
            decoded = request.decode("cp932")
            request.environ.update(decoded.environ)
            decoded.environ = request.environ
            decoded.session = session
            manager.get()['request'] = decoded # hack!
            decoded.is_mobile = True
            directlyProvides(decoded, IMobileRequest)
            decoded.is_docomo = request._ua.is_docomo()
            decoded.registry = request.registry
            decoded._ua = request._ua
            logger.debug("**this is mobile access**")
            response = handler(decoded)
            response = _convert_response_sjis(response)
            if request._ua.is_docomo():
                response = _convert_response_for_docomo(response)
            return response
        else:
            request.is_mobile = False
            logger.debug("**this is pc access**")
            return handler(request)
    return tween
