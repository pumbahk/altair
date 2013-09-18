# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute

class IModelAttributeMetadata(Interface):
    key = Attribute('''''')
    type = Attribute('''''')
    provider = Attribute('''''')

    def get_coercer():
        pass

    def get_display_name(locale):
        pass 

class IModelAttributeMetadataProvider(Interface):
    name = Attribute('''''')

    def __iter__():
        pass

    def __getitem__(key):
        pass

    def __contains__(key):
        pass

class IModelAttributeMetadataProviderRegistry(Interface):
    def queryProviderByName(name):
        pass

    def queryProviderByKey(key):
        pass

    def getProviders():
        pass

    def registerProvider(provider):
        pass


