# -*- encoding:utf-8 -*-

from zope.interface import implementer
from altaircms.interfaces import IModelEvent
from ..solr import api as solr
from ..page import api as pageapi
from altaircms.lib.viewhelpers import FlashMessage

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
    ftsearch = solr.get_fulltext_search(self.request)
    event = self.obj
    for page in event.pages:
        pageapi.ftsearch_register_from_page(self.request, page, ftsearch=ftsearch)
 
def event_delete_solr(self):
    ftsearch = solr.get_fulltext_search(self.request)
    event = self.obj
    for page in event.pages:
        pageapi.ftsearch_delete_register_from_page(self.request, page, ftsearch=ftsearch)

def flash_view_page_url(self):
    fmt = u'<a href="%s">新しく作成/変更されたイベントの詳細画面へ移動</a>'
    mes = fmt % self.request.route_path("event", id=self.obj.id, action="input")
    FlashMessage.success(mes, request=self.request)
