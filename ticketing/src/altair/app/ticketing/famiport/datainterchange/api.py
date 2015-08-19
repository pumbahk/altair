from pyramid.interfaces import IRequest
from .interfaces import IFamiPortFileManagerFactory

def get_famiport_file_manager_factory(request_or_registry):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry

    return registry.queryUtility(IFamiPortFileManagerFactory)
