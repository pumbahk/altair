from .string import *
from .iteration import *
from .datetime_ import *
from .numbers import *

REQUEST_ADAPTERS = [
    lambda request: DateTimeHelper(create_date_time_formatter(request)),
    lambda request: NumberHelper(create_number_formatter(request)),
    ]

class Namespace(object):
    for k, v in globals().items():
        if callable(v):
            locals()[k] = staticmethod(v)

    def __init__(self, request):
        self.adatpers = []
        for adapter_factory in REQUEST_ADAPTERS:
            adapter = adapter_factory(request)
            for k in dir(adapter):
                if not k.startswith('__'):
                    setattr(self, k, getattr(adapter, k))
