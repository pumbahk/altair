# -*- coding:utf-8 -*-
import logging
import re

from urlparse import urljoin
from zope.interface import implementer
from pyramid.security import authenticated_userid, effective_principals
from pyramid.i18n import TranslationString as _
from altair.app.ticketing.users.models import Membership
from altair.sqlahelper import get_db_session
from altair.auth.api import get_plugin_registry
from altair.auth.pyramid import authenticator_prefix
from altair.rakuten_auth.openid import RakutenOpenID
from altair.app.ticketing.project_specific.nogizaka46.auth import NogizakaAuthPlugin
from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin
from altair.rakuten_auth.interfaces import IRakutenOpenIDURLBuilder
from altair.oauth_auth.plugin import OAuthAuthPlugin

logger = logging.getLogger(__name__)

HARDCODED_PRIORITIES = {
    OAuthAuthPlugin: -4,
    RakutenOpenID: -3,
    FCAuthPlugin: -2,
    NogizakaAuthPlugin: 1,
    }

DISPLAY_NAMES = {
    RakutenOpenID: _(u'楽天会員認証'),
    FCAuthPlugin: _(u'FC会員認証'),
    NogizakaAuthPlugin: _(u'キーワード認証'),
    OAuthAuthPlugin: _(u'OAuth認可APIを使った認証'),
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

        for authenticator_name, identity in identities.items():
            logger.debug('authenticator={authenticator_name}, identity={identity}'.format(authenticator_name=authenticator_name, identity=identity))

            plugin_registry = get_plugin_registry(request)
            authenticator = plugin_registry.lookup(authenticator_name)

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
            else:
                authz_identifier = auth_identifier = identity.get('username', None)
                membership = identity.get('membership', None)
                membergroup = identity.get('membergroup', None)
                is_guest = identity.get('is_guest', False)
            reorganized_identities.append({
                'authenticator': authenticator,
                'authenticator_name': authenticator_name,
                'auth_identifier': auth_identifier,
                'authz_identifier': authz_identifier,
                'membership': membership,
                'membergroup': membergroup,
                'is_guest': is_guest,
                })

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
    def __init__(self, proxy_url_pattern, **kwargs):
        self.proxy_url_pattern = proxy_url_pattern

    def extra_verify_url_exists(self, request):
        return True

    def build_base_url(self, request):
        subdomain = request.host.split('.', 1)[0]
        return self.proxy_url_pattern.format(
            subdomain=subdomain
            )

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

