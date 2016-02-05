# encoding: utf-8
import logging
from zope.interface import implementer
from altair.auth.interfaces import IAuthenticator, IMetadataProvider, ILoginHandler
from altair.sqlahelper import get_db_session
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import joinedload
from .models import MemberSet, MemberKind, Member
from .utils import digest_secret

logger = logging.getLogger(__name__)

def get_db_session_from_request(request):
    return get_db_session(request, 'extauth_slave')

@implementer(IAuthenticator, ILoginHandler, IMetadataProvider)
class InternalAuthPlugin(object):
    name = 'internal'
    METADATA_KEY = '%s.metadata' % __name__

    def __init__(self):
        pass

    # ILoginHandler
    def get_auth_factors(self, request, auth_context, credentials):
        return credentials

    # IAuthenticator
    def authenticate(self, request, auth_context, auth_factors):
        credentials = auth_factors.get(self.name)
        if credentials is not None:
            # login
            guest = credentials.get('guest', False)
            if guest:
                userdata = guest_authenticate(request, credentials)
                metadata = None
            else:
                userdata, metadata = nonguest_authenticate(request, credentials)
            if userdata is None:
                return None, None
            request.environ[self.METADATA_KEY] = metadata
            auth_factors = {
                session_keeper.name: { self.name: userdata }
                for session_keeper in auth_context.session_keepers
                }
            return userdata, auth_factors
        else:
            userdata = None
            for session_keeper in auth_context.session_keepers:
                auth_factors_for_session_keeper = auth_factors.get(session_keeper.name)
                if auth_factors_for_session_keeper is not None:
                    _userdata = auth_factors_for_session_keeper.get(self.name)
                    if _userdata is not None:
                        userdata = _userdata
                        break
            if userdata is not None and not userdata['guest']:
                _userdata, metadata = validate_member(request, userdata)
                if _userdata is None:
                    return None, None
                request.environ[self.METADATA_KEY] = metadata
            return userdata, auth_factors

    def get_metadata(self, request, auth_context, identities):
        identity = identities.get(self.name)
        if identity is not None and self.METADATA_KEY in request.environ:
            return request.environ.pop(self.METADATA_KEY)
        else:
            return None

def build_metadata_dict_from_member(member):
    return dict(
        email_1=member.email,
        nick_name=member.name, # XXX
        first_name=member.given_name,
        last_name=member.family_name,
        first_name_kana=member.given_name_kana,
        last_name_kana=member.family_name_kana,
        birthday=member.birthday,
        gender=member.gender,
        country=member.country,
        zip=member.zip,
        prefecture=member.prefecture,
        city=member.city,
        address_1=member.address_1,
        address_2=member.address_2,
        tel_1=member.tel_1,
        tel_2=member.tel_2
        )

def guest_authenticate(request, identity):
    """
    指定メンバーシップにおけるゲストメンバーグループでidentifyする
    """
    member_set_name = identity.get('member_set')
    if member_set_name is None:
        return None

    member_kind_name = identity.get('member_kind')
    if member_kind_name is None:
        return None

    member_kind = get_db_session_from_request(request) \
        .query(MemberKind).join(MemberKind.member_set) \
        .filter(MemberKind.enable_guests != False) \
        .filter(MemberKind.name == member_kind_name) \
        .filter(MemberSet.name == member_set_name) \
        .one()

    if member_kind is None:
        logger.debug('guest member_kind is not found at %s' % member_set_name)
        return None
    return {
        'organization': member_kind.member_set.organization.short_name,
        'host_name': member_kind.member_set.organization.canonical_host_name,
        'member_kind': member_kind.name,
        'member_set': member_set_name,
        'guest': True,
        }

def nonguest_authenticate(request, identity):
    member_set_name = identity.get('member_set')
    auth_identifier = identity.get('auth_identifier')
    if not (member_set_name and auth_identifier):
        logger.debug('identity could not be retrieved because either member_set or username is not provided: %r' % identity)
        return None, None

    try:
        member = get_db_session_from_request(request) \
            .query(Member) \
            .options(joinedload(Member.member_set), joinedload(Member.memberships)) \
            .filter(Member.auth_identifier == auth_identifier) \
            .filter(MemberSet.id == Member.member_set_id) \
            .filter(MemberSet.name == member_set_name) \
            .one()
    except NoResultFound:
        logger.debug('no user found for identity: %r' % identity)
        return None, None
    except MultipleResultsFound:
        logger.error('multiple records found for identity: %r' % identity)
        return None, None

    if not member.enabled:
        logger.debug('Member(auth_identifier=%s) is disabled' % member.auth_identifier)
        return None, None

    if member.member_set.use_password:
        raw_auth_secret = identity.get('auth_secret')
        if raw_auth_secret is None:
            logger.debug('identity could not be verified because auth_secret is not provided: %r' % identity)
            return None, None
        else:
            auth_secret = digest_secret(raw_auth_secret, member.auth_secret[:32])
            if member.auth_secret != auth_secret:
                logger.debug(u'password does not match')
                return None, None
    return (
        {
            'member_id': member.id,
            'organization': member.member_set.organization.short_name,
            'host_name': member.member_set.organization.canonical_host_name,
            'auth_identifier': auth_identifier,
            'member_set': member.member_set.name,
            'guest': False,
            },
        build_metadata_dict_from_member(member)
        )

def validate_member(request, identity):
    member_id = identity.get('member_id')
    if not member_id:
        logger.debug('identity could not be retrieved because member_id is not provided: %r' % identity)
        return None, None
    try:
        member = get_db_session_from_request(request) \
            .query(Member) \
            .options(joinedload(Member.member_set)) \
            .filter(Member.id == member_id) \
            .one()
    except NoResultFound:
        logger.debug('no user found for identity: %r' % identity)
        return None, None

    if not member.enabled:
        logger.debug('Member(auth_identifier=%s) is disabled' % member.auth_identifier)
        return None, None

    return (
        {
            'member_id': member.id,
            'organization': member.member_set.organization.short_name,
            'host_name': member.member_set.organization.canonical_host_name,
            'auth_identifier': member.auth_identifier,
            'member_set': member.member_set.name,
            'guest': False,
            },
        build_metadata_dict_from_member(member)
        )

def includeme(config):
    config.add_auth_plugin(InternalAuthPlugin())
