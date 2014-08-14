from zope.interface import implementer
from repoze.who.interfaces import IIdentifier, IAuthenticator, IChallenger, IMetadataProvider
from .interfaces import IAugmentedWhoAPIFactory, IAugmentedWhoAPI

class DummyDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        return self.request.testing_who_api_name


@implementer(IIdentifier, IAuthenticator, IChallenger, IMetadataProvider)
class DummyPlugin(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def identify(self, environ):
        return environ['return_value_for_identify']

    def forget(self, environ, identity):
        environ['identity_passed_to_forget'] = identity
        return environ['return_value_for_forget']

    def remember(self, environ, identity):
        environ['identity_passed_to_remember'] = identity
        return environ['return_value_for_remember']

    def authenticate(self, environ, identity):
        environ['identity_passed_to_authenticate'] = identity
        return environ['return_value_for_authenticate']

    def challenge(self, environ, status, app_headers, forget_headers):
        environ['status_passed_to_challenge'] = status
        environ['app_headers_passed_to_challenge'] = app_headers
        environ['forget_headers_passed_to_challenge'] = forget_headers
        return environ['return_value_for_challenge']

    def add_metadata(self, environ, identity):
        environ['identity_passed_to_add_metadata'] = identity


class DummySession(dict):
    def save(self):
        pass

def make_augmented_who_api_factory_with_dummy(*args, **kwargs):
    from .facade import AugmentedWhoAPIFactory
    plugin = DummyPlugin(*args, **kwargs)
    return AugmentedWhoAPIFactory(
        authenticators=[('dummy', plugin)],
        challengers=[('dummy', plugin)],
        mdproviders=[('dummy', plugin)]
        )
