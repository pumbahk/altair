# -*- coding:utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class OrganizationSettingBasedWhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        from altair.app.ticketing.core.api import get_organization
        from altair.app.ticketing.models import DBSession
        org = get_organization(self.request)
        DBSession.add(org) # XXX
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

    if auth_type is not None:
        principals.append('auth_type:%s' % auth_type)

    return principals
