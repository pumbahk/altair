from zope.interface import implementer
from .interfaces import (
    IModelAttributeMetadata,
    IModelAttributeMetadataProvider,
    IModelAttributeMetadataProviderRegistry
    )

class ModelAttributeMetadataProviderRegistryError(Exception):
    pass

@implementer(IModelAttributeMetadataProviderRegistry)
class DefaultModelAttributeMetadataProviderRegistry(object):
    def queryProviderByKey(self, key):
        try:
            return self.providers_by_key[key]
        except KeyError:
            raise ModelAttributeMetadataProviderRegistryError(u"No provider that handles '%s' exists" % key)
           
    def queryProviderByName(self, name):
        try:
            return self.providers[name]
        except KeyError:
            raise ModelAttributeMetadataProviderRegistryError(u"No provider that is named '%s' is registered" % name)

    def getProviders(self):
        return self.providers.values() 

    def registerProvider(self, provider):
        provider_name = provider.name
        keys = list(provider)
        if provider_name in self.providers:
            raise ModelAttributeMetadataProviderRegistryError(u"provider that is named '%s' already registered" % provider_name)

        for key in keys:
            if key in self.providers_by_key:
                raise ModelAttributeMetadataProviderRegistryError(u"provider that handles '%s' already registered" % key)

        self.providers[provider_name] = provider
        for key in keys:
            self.providers_by_key[key] = provider

    def __init__(self):
        self.providers = {}
        self.providers_by_key = {}

@implementer(IModelAttributeMetadataProvider)
class DefaultModelAttributeMetadataProvider(object):
    def __iter__(self):
        return iter(self.metadata)

    def __getitem__(self, key):
        return self.metadata[key]

    def __contains__(self, key):
        return key in self.metadata

    def __init__(self, name, metadata_dict):
        metadata = {}
        for key, metadata_dict in metadata_dict.items():
            metadata[key] = DefaultModelAttributeMetadata(
                self, key,
                metadata_dict.get('type', str),
                metadata_dict.get('display_name', {}),
                metadata_dict.get('coercer', None)
                )
        self.name = name
        self.metadata = metadata

@implementer(IModelAttributeMetadata)
class DefaultModelAttributeMetadata(object):
    def __init__(self, provider, key, type, display_name={}, coercer=None):
        self.provider = provider
        self.key = key
        self.type = type
        self.display_name = display_name
        self.coercer = (lambda x: x) if coercer is None else coercer

    def get_coercer(self):
        return self.coercer

    def get_display_name(self, locale):
        return self.display_name.get(locale)

def includeme(config):
    config.add_directive("set_model_metadata_provider_registry", ".config.set_model_metadata_provider_registry")
