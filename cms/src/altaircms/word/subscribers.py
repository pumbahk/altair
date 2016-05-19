# coding: utf-8

from zope.interface import implementer
from altaircms.interfaces import IModelEvent

@implementer(IModelEvent)
class WordCreate(object):
    def __init__(self, request, obj, params=None):
        self.request = request
        self.obj = obj
        self.params = params
