# -*- coding:utf-8 -*-
#
import pickle
import logging
import wsgiref.util
from webob.exc import HTTPFound
from zope.interface import implementer
from altair.auth.interfaces import IChallenger, IAuthenticator, ILoginHandler
from altair.sqlahelper import get_db_session
from .api import login_url, get_memberships
from . import SESSION_KEY

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import altair.app.ticketing.users.models as u_m

logger = logging.getLogger(__name__)

def make_plugin():
    return FCAuthPlugin()

def get_db_session_from_request(request):
    return get_db_session(request, 'slave') # XXX

@implementer(IAuthenticator, IChallenger, ILoginHandler)
class FCAuthPlugin(object):
    name = 'fc_auth'

    def __init__(self):
        pass

    # ILoginHandler
    def get_auth_factors(self, request, auth_context, credentials):
        return credentials

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        logger.debug('authenticate fc_auth')
        credentials = auth_factors.get(self.name)
        if credentials is not None:
            # login
            is_guest = credentials.get('is_guest', False)
            if is_guest:
                logger.debug('authentication for guest')
                userdata = guest_authenticate(request, credentials)
            else:
                logger.debug('authentication for non-guest')
                userdata = nonguest_authenticate(request, credentials)
            if userdata is None:
                return None, None
            auth_factors = {
                session_keeper.name: { 'fc_auth': userdata }
                for session_keeper in auth_context.session_keepers
                }
            return userdata, auth_factors
        else:
            userdata = None
            for session_keeper in auth_context.session_keepers:
                auth_factors_for_session_keeper = auth_factors.get(session_keeper.name)
                if auth_factors_for_session_keeper is not None:
                    _userdata = auth_factors_for_session_keeper.get('fc_auth')
                    if _userdata is not None:
                        userdata = _userdata
                        break
            if userdata is not None and not userdata['is_guest']:
                # revalidate user if not authenticated as a guest
                userdata = nonguest_authenticate(request, userdata)
                if userdata is None:
                    return None, None
            return userdata, auth_factors

    def is_auth_required(self, request):
        return bool(get_memberships(request, get_db_session_from_request(request)))

    # IChallenger
    def challenge(self, request, auth_context, response):
        logger.debug('challenge')
        if not self.is_auth_required(request):
            logger.debug('authentication is not required')
            return
        logger.debug('authentication is required')
        session = request.session.setdefault(SESSION_KEY, {})
        session['return_url'] = request.current_route_path(_query=request.GET)
        request.session.save()
        response.status = 302
        response.location = login_url(request)
        return True

    # IMetadataProvider
    def add_metadata(self, request, identity):
        pass

def guest_authenticate(request, identity):
    """
    指定メンバーシップにおけるゲストメンバーグループでidentifyする
    """
    membership_name = identity.get('membership')
    if membership_name is None:
        return None

    # XXX: 販売区分見ていないがいいのか?
    membergroup = get_db_session_from_request(request).query(u_m.MemberGroup) \
        .filter(u_m.MemberGroup.is_guest==True) \
        .filter(u_m.MemberGroup.membership_id==u_m.Membership.id) \
        .filter(u_m.Membership.name==membership_name) \
        .first()

    if membergroup is None:
        logger.debug('guest membergroup is not found at %s' % membership_name)
        return None
    return {
        'username': 'guest', 
        'membergroup': membergroup.name,
        'membership': membership_name,
        'is_guest': True,
        }

def nonguest_authenticate(request, identity):
    membership_name = identity.get('membership')
    username = identity.get('username')
    if not (membership_name and username):
        logger.debug('identity could not be retrieved because either membership or username is not provided: %r' % identity)
        return None

    member_query = get_db_session_from_request(request).query(u_m.Member) \
        .filter(u_m.Member.auth_identifier == username) \
        .filter(u_m.Membership.id == u_m.Member.membership_id) \
        .filter(u_m.Membership.name == membership_name)

    try:
        member = member_query.one()
    except NoResultFound:
        logger.debug('no user found for identity: %r' % identity)
        return None
    except MultipleResultsFound:
        logger.error('multiple records found for identity: %r' % identity)
        return None

    return {
        'username': username, 
        'membergroup': member.membergroup.name,
        'membership': member.membergroup.membership.name,
        'is_guest': False,
        }
