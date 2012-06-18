from zope.interface import Interface

class IWFinder(Interface):
    def __call__(request, *args, **kwargs):
        pass

class IWRender(Interface):
    pass

