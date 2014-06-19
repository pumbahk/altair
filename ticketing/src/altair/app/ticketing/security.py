# -*- coding:utf-8 -*-
import logging

from pyramid.security import authenticated_userid, effective_principals

logger = logging.getLogger(__name__)

class OrganizationSettingBasedWhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        from altair.app.ticketing.cart.api import get_organization
        org = get_organization(self.request)
        return org.setting.auth_type

def auth_model_callback(identity, request):
    if not isinstance(identity, dict):
        return []
    principals = []
    auth_type = None

    from altair.app.ticketing.fc_auth.plugins import FCAuthPlugin
    from altair.rakuten_auth.plugins import RakutenOpenIDPlugin

    logger.debug('authenticator={authenticator}, identifier={identifier}'.format(**identity))

    if isinstance(identity['authenticator'], FCAuthPlugin):
        # fc_auth固有の処理
        auth_type = 'fc_auth'
        if 'membership' in identity:
            logger.debug('found membership')
            principals.append("membership:%s" % identity['membership'])
        if 'membergroup' in identity:
            logger.debug('found membergroup')
            principals.append("membergroup:%s" % identity['membergroup'])
    elif isinstance(identity['authenticator'], RakutenOpenIDPlugin):
        auth_type = 'rakuten'
        principals.append("membership:rakuten")

    if auth_type is not None:
        principals.append('auth_type:%s' % auth_type)

    return principals

def get_extra_auth_info_from_principals(principals):
    auth_type = None
    membership = None
    membergroup = None
    for principal in principals:
        if principal.startswith('membership:'):
            membership = principal[11:]
        elif principal.startswith('membergroup:'):
            membergroup = principal[12:]
        elif principal.startswith('auth_type:'):
            auth_type = principal[10:]
    return {
        'auth_type': auth_type,
        'membership': membership,
        'membergroup': membergroup,
        }
