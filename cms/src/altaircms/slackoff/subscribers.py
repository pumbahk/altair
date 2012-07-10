# -*- encoding:utf-8 -*-

from zope.interface import implementer
from altaircms.interfaces import IModelEvent

def notify_promotion_create(request, promotion, params=None):
    registry = request.registry
    return registry.notify(PromotionCreate(request, promotion, params))

def notify_promotion_update(request, promotion, params=None):
    registry = request.registry
    return registry.notify(PromotionUpdate(request, promotion, params))

def notify_promotion_delete(request, promotion, params=None):
    registry = request.registry
    return registry.notify(PromotionDelete(request, promotion, params))


@implementer(IModelEvent)
class PromotionCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

@implementer(IModelEvent)
class PromotionUpdate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params
        
@implementer(IModelEvent)
class PromotionDelete(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params

## need async
##
def update_kind(self):
    self.obj.update_kind(self.params["kind_content"])
