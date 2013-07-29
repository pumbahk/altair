from zope.interface import Interface
from zope.interface import Attribute

class IPreviewPermission(Interface):
    def can_preview(request):
        pass

    def has_permission(request):
        pass

class IPreviewRedirect(Interface):
    def on_success(request, handler, permission):
        pass

    def on_failure(request, handler, permission):
        pass

class IPreviewSecret(Interface):
    salt = Attribute("salt")
    def __call__(request, key):
        pass
