# -*- coding:utf-8 -*-
#
import pickle
import logging
import wsgiref.util
from pyramid.threadlocal import get_current_request
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator
from .api import login_url

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

    @property
    def request(self):
        return get_current_request()

    # IIdentifier
    def identify(self, environ):
        req = self.request
        identity = self.get_identity(req)
        logging.debug(identity)

        if identity is None:
            #logger.debug("fc_auth identity failed")
            return None

        if 'repoze.who.plugins.auth_tkt.userid' in identity:
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                if 'membership' in userdata:
                    userdata['identify'] = True
                    logger.debug('fc auth identified %s' % userdata)
                    is_guest = userdata.get('is_guest', False)
                    if is_guest:
                        logger.debug('fc auth this is guest')
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
        if 'repoze.who.plugins.auth_tkt.userid' in identity:
            identity = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))


        is_guest = identity.get('is_guest', False)
        
        if is_guest:
            logger.debug('authenticate fc_auth for guest')
            return guest_authenticate(environ, identity)
        membership = identity.get('membership')
        username = identity.get('username')
        password = identity.get('password')
        is_identify = identity.get('identify', False)

        # 以下の処理も関数にわけるべきか
        if not (membership and username and password) and not is_identify:
            logger.debug('fc_auth identity was not found : %s' % identity)
            return

        user_query = u_m.User.query.filter(
            u_m.UserCredential.auth_identifier==username
            ).filter(
            u_m.Membership.id==u_m.UserCredential.membership_id
            ).filter(
            u_m.Membership.name==membership
            ).filter(
                u_m.User.id==u_m.UserCredential.user_id
            )

        if not is_identify:
            user_query = user_query.filter(
                u_m.UserCredential.auth_secret==password
            )

        user = user_query.first()

        if user is None:
            return

        data = {'username': username, 
            'membergroup': user.member.membergroup.name,
            'membership': user.member.membergroup.membership.name,
            'is_guest': False,
            }
        return pickle.dumps(data).encode('base64')

        
    def is_auth_required(self, environ):
        #return environ.get('ticketing.cart.fc_auth.required')
        request = get_current_request()
        if hasattr(request, 'context') and hasattr(request.context, 'memberships'):
            return bool(request.context.memberships)

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        logger.debug('challenge')
        if not self.is_auth_required(environ):
            logger.debug('fc auth is not required')
            return
        logger.debug('fc auth is required')
        session = environ['session.rakuten_openid']
        session['return_url'] = wsgiref.util.request_uri(environ)
        session.save()
        #return HTTPFound(location=environ['ticketing.cart.fc_auth.login_url'])
        request = get_current_request()
        return HTTPFound(location=login_url(request))

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        pass

def guest_authenticate(environ, identity):
    """
    指定メンバーシップにおけるゲストメンバーグループでidentifyする
    """
    membership_name = identity.get('membership')
    if membership_name is None:
        return None

    membergroup = u_m.MemberGroup.query.filter(
        u_m.MemberGroup.is_guest==True,
    ).filter(
        u_m.MemberGroup.membership_id==u_m.Membership.id
    ).filter(
        u_m.Membership.name==membership_name
    ).first()

    if membergroup is None:
        logger.debug('guest membergroup is not found at %s' % membership_name)
        return None
    data = {'username': u'ゲスト', 
        'membergroup': membergroup.name,
        'membership': membership_name,
        'is_guest': True,
    }

    return pickle.dumps(data).encode('base64')
