from zope.interface import Interface
from zope.interface import Attribute

class IInternalAuthResource(Interface):
    def get_after_login_url(*args, **kwargs):
        """ arguments is same for 'pyramid.request.add_route_path' """

    def login_validate(form):
        pass

    __acl__ = Attribute("__acl__")
