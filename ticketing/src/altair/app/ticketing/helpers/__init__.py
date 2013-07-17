from .base import *
from .admin import *
from .dt import *

REQUEST_ADAPTERS = [
    AdminHelperAdapter
    ]

class Namespace(object):
    for k, v in globals().items():
        if callable(v):
            locals()[k] = staticmethod(v)

    def __init__(self, request):
        self.adapters = []
        for adapter_factory in REQUEST_ADAPTERS:
            adapter = adapter_factory(request)
            for k in dir(adapter):
                if not k.startswith('__'):
                    setattr(self, k, getattr(adapter, k))

