from zope.interface import Interface
from zope.interface import Attribute

class IInternalAuthResource(Interface):
    def get_after_login_url():
        pass
    __acl__ = Attribute("__acl__")

