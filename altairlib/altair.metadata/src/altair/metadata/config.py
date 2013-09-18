# -*- coding:utf-8 -*-
from .interfaces import IModelAttributeMetadataProviderRegistry

def set_model_metadata_provider_registry(config, provider_registry, name=""):
    config.registry.registerUtility(provider_registry, 
                                    IModelAttributeMetadataProviderRegistry, 
                                    name=name)
