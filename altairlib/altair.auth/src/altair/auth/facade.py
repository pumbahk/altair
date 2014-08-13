from zope.interface import implementer
from .interfaces import IAugmentedWhoAPIFactory
from repoze.who.api import API as WhoAPI

class AugmentedWhoAPI(WhoAPI):
    def __init__(self, request, factory, *args, **kwargs):
        super(AugmentedWhoAPI, self).__init__(request, *args, **kwargs)
        self.factory = factory


@implementer(IAugmentedWhoAPIFactory)
class AugmentedWhoAPIFactory(object):
    def __init__(self,
            authenticators=(),
            challengers=(),
            mdproviders=(),
            request_classifier=None,
            challenge_decider=None,
            remote_user_key='REMOTE_USER',
            logger=None):
        self.authenticators = authenticators
        self.challengers = challengers
        self.mdproviders = mdproviders
        self.request_classifier = request_classifier
        self.challenge_decider = challenge_decider
        self.remote_user_key = remote_user_key
        self.logger = logger

    def __call__(self, request, identifiers=()):
        return AugmentedWhoAPI(
            request.environ,
            factory=self,
            identifiers=identifiers,
            authenticators=self.authenticators,
            challengers=self.challengers,
            mdproviders=self.mdproviders,
            request_classifier=self.request_classifier,
            challenge_decider=self.challenge_decider,
            remote_user_key=self.remote_user_key,
            logger=self.logger
            )
