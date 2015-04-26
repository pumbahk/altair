from zope.interface import implementer
from .interfaces import (
    ISessionKeeper,
    IAuthenticator,
    IChallenger,
    ILoginHandler,
    IMetadataProvider,
    )

def dummy_decider(request, classification):
    return request.testing_who_api_name


@implementer(ISessionKeeper, ILoginHandler, IAuthenticator, IChallenger, IMetadataProvider)
class DummyPlugin(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def get_auth_factors(self, request, auth_context, credentials=None):
        if credentials is not None:
            return credentials
        else:
            return request.auth_factors

    def forget(self, request, auth_context, response, auth_factor=None):
        request.auth_factor_passed_to_forget = auth_factor

    def remember(self, request, response, auth_factors=None):
        request.auth_factors_passed_to_remember = auth_factors

    def authenticate(self, request, auth_context, auth_factors):
        request.auth_factors_passed_to_authenticate = auth_factors

    def challenge(self, request, auth_context, response):
        pass

    def get_metadata(self, request, auth_context, identities):
        self.identities_passed_to_get_metadata = identities
        return self.return_value_for_get_metadata


class DummySession(dict):
    def save(self):
        pass
