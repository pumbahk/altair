# -*- coding:utf-8 -*-
import logging
import re

from urlparse import urljoin, urlparse
from urllib import unquote
from zope.interface import implementer
from pyramid.i18n import TranslationString as _
from altair.app.ticketing.users.models import Membership
from altair.sqlahelper import get_db_session
from altair.auth.api import get_plugin_registry, decide
from altair.auth.pyramid import authenticator_prefix
from altair.rakuten_auth.openid import RakutenOpenID
from altair.app.ticketing.authentication.plugins.externalmember import ExternalMemberAuthPlugin, \
    EXTERNALMEMBER_ID_POLICY_NAME
from altair.app.ticketing.authentication.plugins.privatekey import PrivateKeyAuthPlugin
from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin
from altair.oauth_auth.plugin import OAuthAuthPlugin
from altair.rakuten_auth.interfaces import IRakutenOpenIDURLBuilder

logger = logging.getLogger(__name__)

HARDCODED_PRIORITIES = {
    OAuthAuthPlugin: -4,
    RakutenOpenID: -3,
    FCAuthPlugin: -2,
    PrivateKeyAuthPlugin: 1,
    ExternalMemberAuthPlugin: 2,
    }

DISPLAY_NAMES = {
    RakutenOpenID: _(u'楽天会員認証'),
    FCAuthPlugin: _(u'FC会員認証'),
    PrivateKeyAuthPlugin: _(u'キーワード認証'),
    ExternalMemberAuthPlugin: _(u'外部会員番号取得キーワード認証'),
    OAuthAuthPlugin: _(u'OAuth認可APIを使った認証'),
    }

def reorganize_identity(request, authenticator, identity):
    if isinstance(authenticator, RakutenOpenID):
        auth_identifier = authz_identifier = identity['claimed_id']
        membership = 'rakuten'
        membergroup = None
        is_guest = False
    elif isinstance(authenticator, OAuthAuthPlugin):
        auth_identifier = identity['id']
        authz_identifier = identity.get('authz_id') or auth_identifier
        _membership = get_db_session(request, 'slave').query(Membership).filter_by(organization_id=request.organization.id).first()
        membership = _membership.name if _membership is not None else None
        membergroup = identity['authz_kind']
        is_guest = False
        if auth_identifier.startswith(u'acct:'):
            try:
                parsed_auth_identifier = urlparse(auth_identifier)
                g = re.match(ur'^([^@]+)@([^@]+)$', parsed_auth_identifier.path)
                if g is not None:
                    user_part = unquote(g.group(1))
                    user, _, memberset = user_part.partition(u'+')
                    if user == u'*':
                        is_guest = True
            except:
                pass
    else:
        authz_identifier = auth_identifier = identity.get('username', None)
        membership = identity.get('membership', None)
        membergroup = identity.get('membergroup', None)
        is_guest = identity.get('is_guest', False)

    # 外部会員番号取得キーワード認証は authz_identifier (会員番号) に外部会員番号をセットします。
    if isinstance(authenticator, ExternalMemberAuthPlugin):
        authz_identifier = identity.get(EXTERNALMEMBER_ID_POLICY_NAME)

    return {
        'authenticator': authenticator,
        'authenticator_name': authenticator.name,
        'auth_identifier': auth_identifier,
        'authz_identifier': authz_identifier,
        'membership': membership,
        'membergroup': membergroup,
        'is_guest': is_guest,
        }

class AuthModelCallback(object):
    def __init__(self, config):
        self.registry = config.registry
        _priorities = self.registry.settings.get('altair.app.ticketing.security.auth_priorities')
        if _priorities is not None:
            entries = []
            count_per_priority = {}
            for v in re.split(ur'\r\n|\r|\n', _priorities):
                v = v.strip()
                if not v:
                    continue
                pair = re.split(ur'\s+', v)
                priority = int(pair[1]) if len(pair) > 1 else 0
                occurrence = count_per_priority.get(priority, 0)
                entries.append(
                    {
                        'plugin': config.maybe_dotted(pair[0]),
                        'priority': priority,
                        'occurrence': occurrence,
                        }
                    )
                count_per_priority[priority] = occurrence + 1

            c = max(count_per_priority.values())
            priorities = dict((e['plugin'], e['priority'] * c + e['occurrence']) for e in entries)
        else:
            priorities = HARDCODED_PRIORITIES
        self.priorities = priorities
        logger.info('priorities=%r' % priorities)

    def __call__(self, identities, request):
        reorganized_identities = []
        interesting_authenticator_names = decide(request)
        logger.debug('interesting authenticators={authenticators}'.format(authenticators=interesting_authenticator_names))
        plugin_registry = get_plugin_registry(request)
        for authenticator_name, identity in identities.items():
            if interesting_authenticator_names is not None and authenticator_name not in interesting_authenticator_names:
                logger.debug('ignoring authenticator={authenticator_name}, identity={identity}'.format(authenticator_name=authenticator_name, identity=identity))
                continue
                
            logger.debug('authenticator={authenticator_name}, identity={identity}'.format(authenticator_name=authenticator_name, identity=identity))

            authenticator = plugin_registry.lookup(authenticator_name)
            reorganized_identity = reorganize_identity(request, authenticator, identity)
            reorganized_identities.append(reorganized_identity)

        reorganized_identities.sort(key=lambda identity: self.priorities.get(identity['authenticator'].__class__) or 0)
        logger.debug('reorganized_identities=%r' % reorganized_identities)

        principals = []
        membership = None 
        membership_source = None
        membergroup = None
        is_guest = None
        auth_identifier = None
        authz_identifier = None

        for identity in reorganized_identities:
            if auth_identifier is None:
                auth_identifier = identity['auth_identifier'] 
            if authz_identifier is None:
                authz_identifier = identity['authz_identifier'] 
            if membership is None:
                membership = identity['membership']
                membership_source = identity['authenticator_name']
                membergroup = identity.get('membergroup')
            if is_guest is None:
                is_guest = identity['is_guest']

        if auth_identifier is not None:
            principals.append('auth_identifier:%s' % auth_identifier)
        if authz_identifier is not None:
            principals.append('authz_identifier:%s' % authz_identifier)
        if membership is not None:
            principals.append('membership:%s' % membership)
            principals.append('membership_source:%s' % membership_source)
        if membergroup is not None:
            principals.append('membergroup:%s' % membergroup)
        if is_guest:
            principals.append('altair_guest')

        return principals

def get_extra_auth_info_from_principals(principals):
    auth_identifier = None
    authz_identifier = None
    membership = None
    membership_source = None
    membergroup = None
    is_guest = False

    authenticators = []

    for principal in principals:
        if principal.startswith('membership:'):
            membership = principal[11:]
        elif principal.startswith('membership_source:'):
            membership_source = principal[18:]
        elif principal.startswith('membergroup:'):
            membergroup = principal[12:]
        elif principal.startswith('auth_identifier:'):
            auth_identifier = principal[16:]
        elif principal.startswith('authz_identifier:'):
            authz_identifier = principal[17:]
        elif principal == 'altair_guest':
            is_guest = True
        elif principal.startswith(authenticator_prefix):
            authenticators = principal[len(authenticator_prefix):].split('+')
    return {
        'authenticators': authenticators,
        'membership_source': membership_source,
        'auth_identifier': auth_identifier,
        'authz_identifier': authz_identifier,
        'membership': membership,
        'membergroup': membergroup,
        'is_guest': is_guest,
        }

def get_plugin_names(request, predicate=None):
    plugin_registry = get_plugin_registry(request)
    if predicate is None:
        return ((name, DISPLAY_NAMES.get(plugin.__class__, name)) for name, plugin in plugin_registry)
    else:
        return ((name, DISPLAY_NAMES.get(plugin.__class__, name)) for name, plugin in plugin_registry if predicate(plugin))

def get_display_name(request, plugin_name):
    plugin_registry = get_plugin_registry(request)
    plugin = plugin_registry.lookup(plugin_name) if plugin_name is not None else None
    return DISPLAY_NAMES.get(plugin.__class__, plugin.name) if plugin is not None else _(u'(なし)')

@implementer(IRakutenOpenIDURLBuilder)
class RakutenAuthURLBuilder(object):
    def __init__(self, proxy_url_pattern=None, **kwargs):
        self.proxy_url_pattern = proxy_url_pattern

    def extra_verify_url_exists(self, request):
        return True

    def build_base_url(self, request):
        return request.host_url

    def build_return_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.verify').lstrip('/'))

    def build_error_to_url(self, request):
        return urljoin(self.build_base_url(request).rstrip('/') + '/', request.route_path('rakuten_auth.error').lstrip('/'))

    def build_verify_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_extra_verify_url(self, request):
        return request.route_url('rakuten_auth.verify2')


@implementer(IRakutenOpenIDURLBuilder)
class RakutenAuthNoExtraVerifyURLBuilder(object):
    def __init__(self, **kwargs):
        pass

    def extra_verify_url_exists(self, request):
        return False

    def build_return_to_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_error_to_url(self, request):
        return request.route_url('rakuten_auth.error')

    def build_verify_url(self, request):
        return request.route_url('rakuten_auth.verify')

    def build_extra_verify_url(self, request):
        return None


class Authenticated(object):
    def __init__(self, request, plugin, identity, metadata):
        self.request = request
        self.plugin = plugin
        self.identity = identity
        self.metadata = metadata


def rakuten_auth_challenge_success_callback(request, plugin, identity, metadata):
    request.registry.notify(Authenticated(
        request,
        plugin=plugin,
        identity=identity,
        metadata=metadata
        ))
