# encoding: utf-8
from pyramid.security import Everyone, Allow, Authenticated, DENY_ALL

class ExtAuthBase(object):
    __acl__ = [
        (Allow, 'altair.auth.authenticator:rakuten', 'rakuten'),
        (Allow, Authenticated, 'authenticated'),
        DENY_ALL,
        ]

class ExtAuthRoot(ExtAuthBase):
    subtype = None

    def __init__(self, request):
        self.request = request

    def __getitem__(self, subtype):
        return ExtAuthSubTypeResource(self.request, subtype)

class ExtAuthSubTypeResource(ExtAuthBase):
    def __init__(self, request, subtype):
        self.request = request
        self.subtype = subtype
    
    def route_path(self, *args, **kwargs):
        return self.request.route_path(*args, subtype=self.subtype, **kwargs)
    
    def route_url(self, *args, **kwargs):
        return self.request.route_url(*args, subtype=self.subtype, **kwargs)
