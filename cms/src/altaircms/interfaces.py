from zope.interface import Interface

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

