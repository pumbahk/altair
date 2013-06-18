from zope.interface import implementer
from .interfaces import IGlobalLinkSettings

@implementer(IGlobalLinkSettings)
class GlobalLink(object):
    def __init__(self, backend_url, usersite_url):
        self.usersite_url = usersite_url
        self.backend_url = backend_url

    @classmethod
    def from_settings(cls, settings, prefix="altaircms."):
        return cls(settings[prefix+"backend.url"], 
                   settings[prefix+"usersite.url"])

def get_global_link_settings(request):
    return request.registry.getUtility(IGlobalLinkSettings)

# class UsersiteLink(object):
#     def __init__(self, index, scheme="http"):
#         self.index = index
#         if self.index.endswith("/"):
#             self.index = self.index[:-1]
#         self.scheme = scheme

#     def front_page_url(self, request, part):
#         return "{0}://{1}/{2}".format(self.scheme, self.index, part)

#     def feature_page_url(self, request, part):
#         return "{0}://{1}/features/{2}".format(self.scheme, self.index, part)
