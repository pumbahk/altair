from zope.interface import Interface
from zope.interface import Attribute

class IConcrete(Interface):
    def concrete(self):
        pass

class INode(Interface):
    pass

class IConcreteNode(IConcrete, INode):
    def __init__(self, data, config=None):
        pass

    def concrete(self, request=None, config=None, extra_context=None):
        pass

class IBlockTree(Interface):
    Attribute("blocks")

class ICacher(Interface):
    Attribute("fetched")
    Attribute("scanned")
    Attribute("result")

    def scan(self, target):
        pass

    def fetch(self):
        pass

# class IFromDict(Interface):
#     @classmethod
#     def from_dict(cls):
#         pass
# class IToDict(Interface):
#     def to_dict(self):
#         pass
# class IWithDict(IFromDict, IToDict):
#     pass
