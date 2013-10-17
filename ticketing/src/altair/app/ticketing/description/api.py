# -*- coding:utf-8 -*-
from .interfaces import (
    IModelDescription
)

def get_description(request, model):
    name = model.__class__.__name__
    adapter = request.registry.adapters.lookup((), IModelDescription, name=name)
    return adapter(model)
