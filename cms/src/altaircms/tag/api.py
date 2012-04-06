from .interfaces import ITagSearchMap
from altaircms.lib.apiutils import get_registry

def get_tagmanager(classifier, request=None):
    registry = get_registry(request)
    tsmap = registry.queryUtility(ITagSearchMap)
    if tsmap is None:
        return None
    return tsmap[classifier]
