from zope.interface import implementer
from .interfaces import IScopeManager

@implementer(IScopeManager)
class BasicScopeManager(object):
    def __init__(self, scope_items):
        self.scope_items = set(scope_items)

    def exists(self, scope_item):
        return scope_item in self.scope_items 
