from zope.interface import Interface

class IURLBuilder(Interface):
    def build(request, *args, **kwargs):
        pass
