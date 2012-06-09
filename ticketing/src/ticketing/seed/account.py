# -*- coding: utf-8 -*-

from ticketing.seed import DataSet

from organization import OrganizationData
from user import UserData
from ticketing.core.models import *

class AccountData(DataSet):
    class account_1:
        account_type    = AccountTypeEnum.Playguide.v
        name            = u'自社(楽チケ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ぴあ'
        user            = UserData.user_2
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'イープラス'
        user            = UserData.user_3
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_4:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ローソンチケット'
        user            = UserData.user_4
        organization    = OrganizationData.organization_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_5:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ぴあ(楽チケのクライアントデータ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_6:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'イープラス(楽チケのクライアントデータ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_7:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'ローソンチケット(楽チケのクライアントデータ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_3
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_8:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'クライアント4(楽チケのクライアントデータ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_4
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class account_9:
        account_type    = AccountTypeEnum.Promoter.v
        name            = u'クライアント5(楽チケのクライアントデータ)'
        user            = UserData.user_1
        organization    = OrganizationData.organization_5
        updated_at      = datetime.now()
        created_at      = datetime.now()
