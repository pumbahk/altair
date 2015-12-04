from .interfaces import IOAuthNegotiator, IOAuthAPIFactory
from pyramid.interfaces import IRequest


def get_api_factory(request_or_registry, name):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    retval = registry.getUtility(IOAuthAPIFactory, name)
    if retval is None:
        retval = registry.queryUtility(IOAuthAPIFactory)
    return retval
