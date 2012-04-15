# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.account import AccountData
from seed.event import PerformanceData
from ticketing.products.models import StockHolder
from datetime import datetime

class StockHolderData(DataSet):
    class stockholder_1:
        name = u'営業枠'
        performance = PerformanceData.performance_1
        account = AccountData.account_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
