# -*- coding:utf-8 -*-
#
import pickle
import logging
import wsgiref.util
from webob.exc import HTTPFound
from zope.interface import implementer
from repoze.who.api import get_api as get_who_api
from repoze.who.interfaces import IIdentifier, IChallenger, IAuthenticator
from altair.auth.api import get_current_request
from altair.sqlahelper import get_db_session
from .api import login_url, get_memberships
from . import SESSION_KEY

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import altair.app.ticketing.users.models as u_m

logger = logging.getLogger(__name__)

def make_plugin(rememberer_name, sha1salt):
    return FCAuthPlugin(rememberer_name=rememberer_name)

def get_db_session_from_request(request):
    return get_db_session(request, 'slave') # XXX

@implementer(IIdentifier, IAuthenticator, IChallenger)
class FCAuthPlugin(object):
    def __init__(self, rememberer_name):
        self.rememberer_name = rememberer_name

    def _get_rememberer(self, environ):
        #rememberer = environ['repoze.who.plugins'][self.rememberer_name]

        api = get_who_api(environ)
        rememberer = api.name_registry[self.rememberer_name]
        return rememberer

    def get_identity(self, req):
        rememberer = self._get_rememberer(req.environ)
        return rememberer.identify(req.environ)

    # IIdentifier
    def identify(self, environ):
        req = get_current_request(environ)
        identity = self.get_identity(req)
        logging.debug(identity)

        if identity is not None and 'repoze.who.plugins.auth_tkt.userid' in identity:
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                if userdata is not None and 'membership' in userdata:
                    userdata['identify'] = True
                    logger.debug('identified %s' % userdata)
                    is_guest = userdata.get('is_guest', False)
                    if is_guest:
                        logger.debug('this is guest')
                    return userdata
            except Exception, e:
                logger.exception(e)

        return None


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
            try:
                userdata = pickle.loads(identity['repoze.who.plugins.auth_tkt.userid'].decode('base64'))
                # XXX: userdata が None であってもここでトラップしてもらう、あまり良いコードではない
                userdata.pop('login', None)
            except:
                logger.exception('unable to retrieve userdata from identity: %r' % identity)
                return None
        else:
            # これは特殊なケース。challenge view から login() が呼ばれたときは
            # identity に必要な情報が全部詰まっているので、userdata = identity とする
            if not identity.get('login', False):
                return None
            userdata = identity
        is_guest = userdata.get('is_guest', False)
        if is_guest:
            logger.debug('authentication for guest')
            userdata = guest_authenticate(environ, identity, userdata)
        else:
            logger.debug('authentication for non-guest')
            userdata = nonguest_authenticate(environ, identity, userdata)
        if userdata is None:
            return None
        return pickle.dumps(userdata).encode('base64')
        
    def is_auth_required(self, environ):
        request = get_current_request(environ)
        return bool(get_memberships(request, get_db_session_from_request(request)))

    # IChallenger
    def challenge(self, environ, status, app_headers, forget_headers):
        logger.debug('challenge')
        if not self.is_auth_required(environ):
            logger.debug('authentication is not required')
            return
        logger.debug('authentication is required')
        request = get_current_request(environ)
        session = request.session.setdefault(SESSION_KEY, {})
        session['return_url'] = wsgiref.util.request_uri(environ)
        request.session.save()
        request = get_current_request(environ)
        return HTTPFound(location=login_url(request))

    # IMetadataProvider
    def add_metadata(self, environ, identity):
        pass

def guest_authenticate(environ, identity, userdata):
    """
    指定メンバーシップにおけるゲストメンバーグループでidentifyする
    """
    req = get_current_request(environ)
    membership_name = userdata.get('membership')
    if membership_name is None:
        return None

    # XXX: 販売区分見ていないがいいのか?
    membergroup = get_db_session_from_request(req).query(u_m.MemberGroup) \
        .filter(u_m.MemberGroup.is_guest==True) \
        .filter(u_m.MemberGroup.membership_id==u_m.Membership.id) \
        .filter(u_m.Membership.name==membership_name) \
        .first()

    if membergroup is None:
        logger.debug('guest membergroup is not found at %s' % membership_name)
        return None
    return {
        'username': u'ゲスト', 
        'membergroup': membergroup.name,
        'membership': membership_name,
        'is_guest': True,
        }

def nonguest_authenticate(environ, identity, userdata):
    req = get_current_request(environ)
    membership_name = userdata.get('membership')
    username = userdata.get('username')
    is_identify = userdata.get('identify', False)
    if not (membership_name and username):
        logger.debug('identity could not be retrieved because either membership or username is not provided: %r' % identity)
        return None

    # identity には auth_identifier しか含まれていないので
    # クッキーを使って identity を保存する場合には、そのクッキーが署名付きでなかったり
    # salt が漏れて偽造されるなどするとなりすましが可能である
    user_query =  get_db_session_from_request(req).query(u_m.User) \
        .filter(u_m.UserCredential.auth_identifier == username) \
        .filter(u_m.Membership.id == u_m.UserCredential.membership_id) \
        .filter(u_m.Membership.name == membership_name) \
        .filter(u_m.User.id == u_m.UserCredential.user_id) \

    try:
        user = user_query.one()
    except NoResultFound:
        logger.debug('no user found for identity: %r' % identity)
        return None
    except MultipleResultsFound:
        logger.error('multiple records found for identity: %r' % identity)
        return None

    if user.member is None:
        logger.debug('no corresponding member record for identity: %r' % identity)
        return None

    return {
        'username': username, 
        'membergroup': user.member.membergroup.name,
        'membership': user.member.membergroup.membership.name,
        'is_guest': False,
        }
