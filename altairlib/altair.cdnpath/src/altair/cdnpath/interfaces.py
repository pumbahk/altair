from zope.interface import Interface
from zope.interface import Attribute

class IStaticURLInfoFactory(Interface):
    def __call__():
        pass
