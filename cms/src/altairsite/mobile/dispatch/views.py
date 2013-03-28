from pyramid.interfaces import IRouter
from pyramid.httpexceptions import HTTPNotFound

def dispatch_view(context, request):
    if "return_twice" in request.environ:
        raise HTTPNotFound()
    request.environ["PATH_INFO"] = "/mobile/"+request.environ["PATH_INFO"].lstrip("/")
    request.environ["return_twice"] = True
    return request.registry.getUtility(IRouter).handle_request(request)
