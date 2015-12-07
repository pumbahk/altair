from pyramid.interfaces import IRequest
from .interfaces import IOAuthProvider, IOpenIDProvider

def get_oauth_provider(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IOAuthProvider)

def get_openid_provider(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IOpenIDProvider)
