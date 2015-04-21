# -*- coding:utf-8 -*-
import logging
import re

from pyramid.security import authenticated_userid, effective_principals
from altair.auth.api import get_plugin_registry
from altair.auth.pyramid import authenticator_prefix
from altair.rakuten_auth.openid import RakutenOpenID
from altair.app.ticketing.project_specific.nogizaka46.auth import NogizakaAuthPlugin
from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin

logger = logging.getLogger(__name__)

HARDCODED_PRIORITIES = {
    RakutenOpenID: -3,
    FCAuthPlugin: -2,
    NogizakaAuthPlugin: 1,
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

            membership = identity.get('membership', None)
            if isinstance(authenticator, RakutenOpenID):
                membership = 'rakuten'
                auth_identifier = identity['claimed_id']
            else:
                auth_identifier = identity.get('username', None)
            reorganized_identities.append({
                'authenticator': authenticator,
                'authenticator_name': authenticator_name,
                'auth_identifier': auth_identifier,
                'membership': membership,
                'membergroup': identity.get('membergroup', None),
                'is_guest': identity.get('is_guest', False),
                })

        reorganized_identities.sort(key=lambda identity: self.priorities.get(identity['authenticator'].__class__) or 0)
        logger.debug('reorganized_identities=%r' % reorganized_identities)

        principals = []
        membership = None 
        membership_source = None
        membergroup = None
        is_guest = None
        auth_identifier = None

        for identity in reorganized_identities:
            if auth_identifier is None:
                auth_identifier = identity['auth_identifier'] 
            if membership is None:
                membership = identity['membership']
                membership_source = identity['authenticator_name']
                membergroup = identity.get('membergroup')
            if is_guest is None:
                is_guest = identity['is_guest']

        if auth_identifier is not None:
            principals.append('auth_identifier:%s' % auth_identifier)
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
            # membergroup は fc_auth でのみ提供されることを期待
            membergroup = principal[12:]
        elif principal.startswith('auth_identifier:'):
            auth_identifier = principal[16:]
        elif principal == 'altair_guest':
            is_guest = True
        elif principal.startswith(authenticator_prefix):
            authenticators = principal[len(authenticator_prefix):].split('+')
    return {
        'authenticators': authenticators,
        'membership_source': membership_source,
        'auth_identifier': auth_identifier,
        'membership': membership,
        'membergroup': membergroup,
        'is_guest': is_guest,
        }
