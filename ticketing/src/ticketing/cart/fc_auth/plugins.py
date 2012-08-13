#

import logging
import webob
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator

import ticketing.users.models as u_m

logger = logging.getLogger(__name__)

def make_plugin():
    pass


@implementer(IIdentifier, IAuthenticator, IChallenger)
class FCAuthPlugin(object):


    # IIdentifier
    def identify(self, environ):
        pass

    # IIdentifier
    def remember(self, environ, identity):
        pass

    # IIdentifier
    def forget(self, environ, identity):
        pass

    # IAuthenticator
    def authenticate(self, environ, identity):
        logger.debug('authenticate fc_auth')
        membership = identity.get('membership')
        username = identity.get('username')
        password = identity.get('password')

        if not (membership and username and password):
            logger.debug('fc_auth identity was not found : %s' % identity)
            return

        user = u_m.User.query.filter(
            u_m.UserCredential.auth_identifier==username
            ).filter(
            u_m.UserCredential.auth_secret==password
            ).filter(
                u_m.Membership.id==u_m.UserCredential.membership_id
                ).filter(
                u_m.Membership.name==membership
                ).filter(
                    u_m.User.id==u_m.UserCredential.user_id
                ).one()

        return user



    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        pass

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        pass
