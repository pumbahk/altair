from pyramid.interfaces import IRouter
from pyramid.httpexceptions import HTTPNotFound

MOBILE_PREFIX = '/mobile'


def mobile_route_path(request):
    def _(*args, **kwargs):
        retval = request.route_path(*args, **kwargs)
        if retval.startswith(MOBILE_PREFIX):
            retval = retval[len(MOBILE_PREFIX):]
        return retval
    return _

def dispatch_view(context, request):
    if "return_twice" in request.environ:
        raise HTTPNotFound()
    request.environ["PATH_INFO"] = MOBILE_PREFIX + "/" + request.environ["PATH_INFO"].lstrip("/")
    request.environ["return_twice"] = True
    request.set_property(mobile_route_path, 'mobile_route_path')
    return request.registry.getUtility(IRouter).handle_request(request)
