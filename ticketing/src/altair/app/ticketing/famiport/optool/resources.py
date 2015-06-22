from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify

class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'administrator', 'administrator'),
        (Allow, 'administrator', 'operator'),
        (Allow, 'operator', 'operator'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request


class TopResource(BaseResource):
    pass


class ExampleResource(BaseResource):
    pass

class SearchResource(BaseResource):
    pass