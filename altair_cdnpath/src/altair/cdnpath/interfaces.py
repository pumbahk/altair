from zope.interface import Interface
from zope.interface import Attribute

class ICDNStaticPathFactory(Interface):
    def __call__(request):
        pass

class ICDNStaticPath(Interface):
    request = Attribute("request")
    def static_path(path, **kwargs):
        pass
    def static_url(path, **kwargs):
        pass
