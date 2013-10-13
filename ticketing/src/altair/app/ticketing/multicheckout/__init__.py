# -*- coding:utf-8 -*-

""" マルチ決済モジュール
"""
import logging
from zope.interface import implementer

from altair.multicheckout.interfaces import IMulticheckoutSetting

import altair.app.ticketing.core.models as core_models

logger = logging.getLogger(__name__)

def includeme(config):
    config.include('altair.multicheckout')
    config.set_multicheckout_setting_factory(get_multicheckout_setting)

# appの実装
def get_multicheckout_setting(request, override_name=None, organization_id=None):
    import altair.app.ticketing.core.api as core_api
    import altair.app.ticketing.core.models as core_models

    logger.info('get_multicheckout_setting override_name = %s, request_host = %s' % (override_name, request.host))
    if override_name:
        os = core_models.OrganizationSetting.query.filter_by(multicheckout_shop_name=override_name).one()
    else:
        if organization_id != None:
            os = core_Models.OrganizationSetting.query.filter_by(organization_id=organization_id).one()
        else:
            organization = core_api.get_organization(request)
            os = organization.setting
    return MulticheckoutSetting(os)

# これは app で実装する
@implementer(IMulticheckoutSetting)
class MulticheckoutSetting(object):
    def __init__(self, organization_setting):
        self.organization_setting = organization_setting

    @property
    def shop_name(self):
        return self.organization_setting.multicheckout_shop_name

    @property
    def shop_id(self):
        return self.organization_setting.multicheckout_shop_id

    @property
    def auth_id(self):
        return self.organization_setting.multicheckout_auth_id

    @property
    def auth_password(self):
        return self.organization_setting.multicheckout_auth_password

# cancel_authで使っている
def get_multicheckout_settings(request):

    return [MulticheckoutSetting(os) 
            for os in core_models.OrganizationSetting.all() 
            if os.multicheckout_shop_id and os.multicheckout_shop_name]

