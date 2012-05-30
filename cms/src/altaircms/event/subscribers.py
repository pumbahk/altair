from zope.interface import implementer
from altaircms.interfaces import IModelEvent
from . import api

def notify_event_create(request, event, params=None):
    registry = request.registry
    return registry.notify(EventCreate(request, event, params))

def notify_event_update(request, event, params=None):
    registry = request.registry
    return registry.notify(EventUpdate(request, event, params))

def notify_event_delete(request, event, params=None):
    registry = request.registry
    return registry.notify(EventDelete(request, event, params))

@implementer(IModelEvent)
class EventCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class EventUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params
        
@implementer(IModelEvent)
class EventDelete(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

## need async
##
def event_register_solr(self): # self is EventCreate/EventUpdate
    event = self.obj
    for page in event.pages:
        api.ftsearch_register_from_page(self.request, page)
 
def event_delete_solr(self):
    event = self.obj
    for page in event.pages:
        api.ftsearch_delete_register_from_page(self.request, page)
