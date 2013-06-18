from pyramid.interfaces import IRouter
from pyramid.httpexceptions import HTTPNotFound

SMARTPHONE_PREFIX = '/smartphone'


def smartphone_route_path(request):
    def _(*args, **kwargs):
        retval = request.route_path(*args, **kwargs)
        if retval.startswith(SMARTPHONE_PREFIX):
            retval = retval[len(SMARTPHONE_PREFIX):]
        return retval
    return _

def dispatch_view(context, request):
    if "return_twice" in request.environ:
        raise HTTPNotFound()
    request.environ["PATH_INFO"] = SMARTPHONE_PREFIX + "/" + request.environ["PATH_INFO"].lstrip("/")
    request.environ["return_twice"] = True
    request.set_property(smartphone_route_path, 'smartphone_route_path')
    return request.registry.getUtility(IRouter).handle_request(request)
