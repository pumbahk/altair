from zope.interface import Interface

class IAccessKeyGetter(Interface):
    def __call__(request, key):
        pass

