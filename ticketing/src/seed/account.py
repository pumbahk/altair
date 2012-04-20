# -*- coding: utf-8 -*-

from seed import DataSet
from ticketing.models import *
from ticketing.events.models import *

class AccountData(DataSet):
    class ticketstar:
        account_type    = AccountTypeEnum.Playguide.v
        user            = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_1:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
