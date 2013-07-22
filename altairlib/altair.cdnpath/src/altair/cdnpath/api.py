from pyramid.interfaces import IRequest
from .interfaces import ICDNStaticPathFactory

## reify
# def cached_factory(request, cachename, gen):
#     v = getattr(request, cachename, None)
#     if v:
#         return v
#     v = gen(request)
#     setattr(request, cachename, v)
#     return v

def get_cdn_static_path(request):
    factory = request.registry.adapters.lookup(IRequest, ICDNStaticPathFactory, name="", default=None)
    return factory(request)
