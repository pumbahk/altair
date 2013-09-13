# -*- coding:utf-8 -*-
from .interfaces import IModelAttributeMetadataProviderRegistry
from pyramid.interfaces import IRequest

def get_metadata_provider_registry(request_or_registry, name=""):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IModelAttributeMetadataProviderRegistry, name=name)

