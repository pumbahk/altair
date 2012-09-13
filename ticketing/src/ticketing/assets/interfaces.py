from zope.interface import Interface

class IAssetResolver(Interface):
    def resolve(spec):
        pass
