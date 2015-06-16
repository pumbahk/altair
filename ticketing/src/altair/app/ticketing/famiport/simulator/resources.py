from pyramid.security import Allow, Deny, Authenticated, DENY_ALL
from pyramid.decorator import reify

class BaseResource(object):
    __acl__ = [
        (Allow, Authenticated, 'authenticated'),
        (Allow, 'client_code_provided', 'client_code_provided'),
        DENY_ALL,
        ]

    def __init__(self, request):
        self.request = request

class FamiPortResource(BaseResource):
    @reify
    def store_code(self):
        return self.request.authenticated_userid

class FamiPortServiceResource(FamiPortResource):
    @reify
    def client_code(self):
        return self.request.session['client_code']

