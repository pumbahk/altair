# -*- coding:utf-8 -*-
import logging

from pyramid.security import authenticated_userid, effective_principals
from altair.auth.api import get_plugin_registry
from altair.auth.pyramid import authenticator_prefix
from altair.rakuten_auth.openid import IRakutenOpenID
from altair.app.ticketing.project_specific.nogizaka46.auth import NogizakaAuthPlugin
from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin

logger = logging.getLogger(__name__)

priorities = {
    'rakuten': -3,
    'fc_auth': -2,
    'nogizaka46': 1,
    }

def auth_model_callback(identities, request):
    reorganized_identities = []

    for authenticator_name, identity in identities.items():
        logger.debug('authenticator={authenticator_name}, identity={identity}'.format(authenticator_name=authenticator_name, identity=identity))

        plugin_registry = get_plugin_registry(request)
        authenticator = plugin_registry.lookup(authenticator_name)

        membership = identity.get('membership', None)
        if IRakutenOpenID.providedBy(authenticator):
            membership = 'rakuten'
            auth_identifier = identity['claimed_id']
        elif isinstance(authenticator, NogizakaAuthPlugin):
            auth_identifier = identity['username']
        elif isinstance(authenticator, FCAuthPlugin):
            auth_identifier = identity['username']
        else:
            auth_identifier = identity.get('username', None)
        reorganized_identities.append({
            'authenticator_name': authenticator_name,
            'auth_identifier': auth_identifier,
            'membership': membership,
            'membergroup': identity.get('membergroup', None),
            'is_guest': identity.get('is_guest', False),
            })

    reorganized_identities.sort(key=lambda identity: priorities.get(authenticator_name) or 0)

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
        if membergroup is None:
            membergroup = identity['membergroup']
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
