from zope.interface import Interface
from pyramid.interfaces import IAssetDescriptor

class IAssetResolver(Interface):
    def resolve(spec):
        pass

class IWritableAssetDescriptor(IAssetDescriptor):
    def write(buf):
        pass
