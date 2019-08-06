import logging

from altair.auth import IAuthenticator
from zope.interface import implementer

logger = logging.getLogger(__name__)


@implementer(IAuthenticator)
class TicketingKeyBaseAuthPlugin(object):
    def __init__(self, backend):
        self.backend = backend

    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('%s: authenticate', self.__class__.__name__)

        auth_factor = {}
        for _auth_factor in auth_factors.values():
            auth_factor.update(_auth_factor)

        opaque = auth_factor.get(self.name)
        identity = self.backend(request, opaque)
        if identity is None:
            logger.debug('%s: authentication failed', self.__class__.__name__)
            return None, None

        session_base_auth_factors = {}
        for session_keeper in auth_context.session_keepers:
            session_base_auth_factors[session_keeper.name] = {self.name: opaque}
        return identity, session_base_auth_factors

    def get_auth_factors(self, request, auth_context, credentials):
        return credentials
