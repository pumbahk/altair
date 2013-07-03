from zope.interface import Interface, Attribute

class IOrderedProductAttributeMetadata(Interface):
    key = Attribute('''''')
    type = Attribute('''''')
    provider = Attribute('''''')

    def get_coercer():
        pass

    def get_display_name(locale):
        pass 

class IOrderedProductAttributeMetadataProvider(Interface):
    name = Attribute('''''')

    def __iter__():
        pass

    def __getitem__(key):
        pass

    def __contains__(key):
        pass

class IOrderedProductAttributeMetadataProviderRegistry(Interface):
    def queryProviderByName(name):
        pass

    def queryProviderByKey(key):
        pass

    def getProviders():
        pass

    def registerProvider(provider):
        pass


