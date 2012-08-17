#
import pickle
import logging
import wsgiref.util
import webob
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator

import ticketing.users.models as u_m

logger = logging.getLogger(__name__)

def make_plugin(rememberer_name, sha1salt):
    return FCAuthPlugin(rememberer_name=rememberer_name)


@implementer(IIdentifier, IAuthenticator, IChallenger)
class FCAuthPlugin(object):
    def __init__(self, rememberer_name):
        self.rememberer_name = rememberer_name

    def _get_rememberer(self, environ):
        rememberer = environ['repoze.who.plugins'][self.rememberer_name]
        return rememberer

    def get_identity(self, req):
        rememberer = self._get_rememberer(req.environ)
        return rememberer.identify(req.environ)

    # IIdentifier
    def identify(self, environ):
        req = webob.Request(environ)
        identity = self.get_identity(req)
        logging.debug(identity)

        if identity is None:
            logger.debug("identity failed")
            return None

        if 'repoze.who.plugins.auth_tkt.userid' in identity:
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                if 'membership' in userdata:
                    return userdata
            except Exception, e:
                logger.exception(e)


    # IIdentifier
    def remember(self, environ, identity):
        logger.debug('remember identity')
        rememberer = self._get_rememberer(environ)
        return rememberer.remember(environ, identity)

    # IIdentifier
    def forget(self, environ, identity):
        rememberer = self._get_rememberer(environ)
        return rememberer.forget(environ, identity)


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

        if user is None:
            return

        data = {'username': username, 'membership': membership}
        return pickle.dumps(data).encode('base64')



    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        if not environ.get('ticketing.cart.fc_auth.required'):
            return
        session = environ['session.rakuten_openid']
        session['return_url'] = wsgiref.util.request_uri(environ)
        session.save()
        return HTTPFound(location=environ['ticketing.cart.fc_auth.login_url'])

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        pass
