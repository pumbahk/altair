from zope.interface import implementer
from ..interfaces import IAPIContext
from ..authentication.apikey.api import get_apikeyentry
from pyramid.interfaces import IRootFactory

@implementer(IAPIContext)
class APIContext(object):
    __name__ = 'api'

    # @property
    # def __parent__(self):
    #     reg = self.request.registry
    #     return reg.queryUtility(IRootFactory)(self.request)

    def __init__(self, request):
        self.request = request
        # assign the APIKeyEntry object if the API request is being made
        self.apikeyentry = get_apikeyentry(request)


        reg = self.request.registry
        parent = reg.queryUtility(IRootFactory)(self.request)
        if parent and hasattr(parent, "__acl__"):
            self.__acl__ = parent.__acl__
