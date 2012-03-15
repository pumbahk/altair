# -*- coding: utf-8 -*-

from seed import DataSet
from ticketing.models import *
from ticketing.models.boxoffice import *
from ticket import TicketerData

class AccountData(DataSet):
    class ticketstar:
        account_type    = AccountTypeEnum.Playguide.v
        user            = None
        ticketer        = TicketerData.ticketstar
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_1:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_2:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class account_3:
        account_type    = AccountTypeEnum.Promoter.v
        user            = None
        ticketer        = TicketerData.ticketer_3
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1