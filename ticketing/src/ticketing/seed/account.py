# -*- coding: utf-8 -*-

from ticketing.seed import DataSet

from organization import OrganizationData
from user import UserData
from ticketing.models import *
from ticketing.events.models import *

class AccountData(DataSet):
    class account_1:
        account_type    = AccountTypeEnum.Playguide.v
        name            = u'自社'
        user            = UserData.user_1
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ぴあ'
        user            = UserData.user_2
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'イープラス'
        user            = UserData.user_3
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_4:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ローソンチケット'
        user            = UserData.user_4
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
