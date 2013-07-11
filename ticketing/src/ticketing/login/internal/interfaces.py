from zope.interface import Interface
from zope.interface import Attribute

class IInternalAuthResource(Interface):
    def get_after_login_url(*args, **kwargs):
        """ arguments is same for 'pyramid.request.add_route_path' """
    __acl__ = Attribute("__acl__")

