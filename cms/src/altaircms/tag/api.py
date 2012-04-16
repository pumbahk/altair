from .interfaces import ITagManager
from altaircms.lib.apiutils import get_registry

def get_tagmanager(classifier, request=None):
    registry = get_registry(request)
    return registry.queryUtility(ITagManager, classifier)

def put_tags(obj, classifier, tags, private_tags, request):
    manager = get_tagmanager(classifier, request=request)
    manager.replace_tags(obj, tags, True)
    manager.replace_tags(obj, private_tags, False)

def tags_to_string(tags):
    return u', '.join(tag.label for tag in tags)
