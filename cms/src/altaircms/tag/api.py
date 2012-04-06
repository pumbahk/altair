from .interfaces import ITagManager
from altaircms.lib.apiutils import get_registry

def get_tagmanager(classifier, request=None):
    registry = get_registry(request)
    return registry.queryUtility(ITagManager, classifier)
