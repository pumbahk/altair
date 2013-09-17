# -*- coding:utf-8 -*-
from .interfaces import IModelAttributeMetadataProviderRegistry
from pyramid.interfaces import IRequest

def get_metadata_provider_registry(request_or_registry, name=""):
    if IRequest.providedBy(request_or_registry):
        registry = request_or_registry.registry
    else:
        registry = request_or_registry
    return registry.queryUtility(IModelAttributeMetadataProviderRegistry, name=name)

def with_provided_values_iterator(metadata_provider_registry, itr, locale="ja_JP"):
    attributes = []
    for key, value in itr:
        metadata = None
        try:
            metadata = metadata_provider_registry.queryProviderByKey(key)[key]
        except:
            pass
        if metadata is not None:
            display_name = metadata.get_display_name(locale)
            coerced_value = metadata.get_coercer()(value)
        else:
            display_name = key
            coerced_value = value

        attributes.append((display_name, key, coerced_value))
    attributes = sorted(attributes, key=lambda x: x[0])
    return attributes

