from zope.interface import implementer
from ..interfaces import IAPIContext
from ..authentication.apikey.api import get_apikeyentry

@implementer(IAPIContext)
class APIContext(object):
    __name__ = 'api'

    @property
    def __parent__(self):
        return self.request.config.root_factory(self.request)

    def __init__(self, request):
        self.request = request
        # assign the APIKeyEntry object if the API request is being made
        self.apikeyentry = get_apikeyentry(request)

