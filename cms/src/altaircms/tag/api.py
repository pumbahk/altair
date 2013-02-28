from .tagname import TagNameResolver
from .interfaces import ITagManager, ISystemTagManager
from altaircms.subscribers import notify_model_create
from pyramid.threadlocal import get_current_registry

def get_tagmanager(classifier, request=None):
    registry = request.registry if request else get_current_registry()
    return registry.getUtility(ITagManager, classifier)

def get_system_tagmanager(classifier, request=None):
    registry = request.registry if request else get_current_registry()
    return registry.getUtility(ISystemTagManager, classifier)

def get_tagname_resolver(request):
    return TagNameResolver(request)

def put_tags(obj, classifier, tags, private_tags, request):
    manager = get_tagmanager(classifier, request=request)
    tags = manager.replace_tags(obj, tags, True, organization_id=request.organization.id)
    private_tags = manager.replace_tags(obj, private_tags, False, organization_id=request.organization.id)
    ## put organization id
    notify_created_tags(request, tags)
    notify_created_tags(request, private_tags)

def put_system_tags(obj, classifier, tags, request):
    manager = get_system_tagmanager(classifier, request=request)
    manager.replace_tags(obj, tags, True, organization_id=None)

def notify_created_tags(request, tags):
    for t in tags:
        notify_model_create(request, t, {})

## move to util?
def string_from_tags(tags, separator=u", "):
    return separator.join(tag.label for tag in tags)
tags_to_string = string_from_tags

def tags_from_string(tagstring, separator=u","):
    tags = [e.strip() for e in tagstring.split(separator)]
    return [k for k in tags if k]
