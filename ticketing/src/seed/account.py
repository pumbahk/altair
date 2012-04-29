# -*- coding: utf-8 -*-

from seed import DataSet

from seed.organization import OrganizationData
from ticketing.models import *
from ticketing.events.models import *

class AccountData(DataSet):
    class account_1:
        account_type    = AccountTypeEnum.Playguide.v
        user            = None
        organization    = OrganizationData.organization_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        organization    = OrganizationData.organization_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        organization    = OrganizationData.organization_3
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_4:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        organization    = OrganizationData.organization_4
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
