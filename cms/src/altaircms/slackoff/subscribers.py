# -*- encoding:utf-8 -*-

from zope.interface import implementer
from altaircms.interfaces import IModelEvent

def notify_topic_create(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicCreate(request, topic, params))

def notify_topic_update(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicUpdate(request, topic, params))

def notify_topic_delete(request, topic, params=None):
    registry = request.registry
    return registry.notify(TopicDelete(request, topic, params))


@implementer(IModelEvent)
class TopicCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class TopicUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params
        
@implementer(IModelEvent)
class TopicDelete(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

## need async
##
from altaircms.tag.api import put_tags, tags_from_string
def update_kind(self):
    tags = tags_from_string(self.params["tag_content"])
    put_tags(self.obj, self.obj.__tablename__, tags, [], self.request)
