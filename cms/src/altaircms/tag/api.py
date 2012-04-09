from .interfaces import ITagSearchMap
from pyramid.threadlocal import get_current_registry

def _get_registry(request):
    if request:
        return request.registry
    else:
        return get_current_registry()

def get_tagmanager(classfier, request=None):
    registry = _get_registry(request)
    tsmap = registry.queryUtility(ITagSearchMap, None)
    if tsmap is None:
        return None
    return tsmap[classfier]
