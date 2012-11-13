import uamobile
import logging
from zope.interface import directlyProvides
from zope.interface import Interface
from pyramid.threadlocal import manager
from pyramid.response import Response
logger = logging.getLogger(__name__)

class IMobileRequest(Interface):
    """ mobile request interface"""

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

def mobile_request_factory(handler, registry):
    def tween(request):
        #directlyProvides(request, IMobileRequest)
        return handler(request)
    return tween
    
def mobile_encoding_convert_factory(handler, registry):
    def tween(request):
        request._ua = uamobile.detect(request.environ)
        debug_mobile = request.registry.settings.get('altair.debug_mobile', False)

        if not request._ua.is_nonmobile():
            ## DeprecationWarning: Use req = req.decode('cp932')
            try:
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
            except UnicodeDecodeError as e:
                logger.warning(str(e))
                return Response(status=400, body=str(e))
        else:
            request.is_mobile = False
            logger.debug("**this is pc access**")
            return handler(request)
    return tween
