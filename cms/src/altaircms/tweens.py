from altaircms.interfaces import ICMSRequest
from zope.interface import directlyProvides

def cms_request_factory(handler, registry):
    def tween(request):
        directlyProvides(request, ICMSRequest)
        return handler(request)
    return tween
