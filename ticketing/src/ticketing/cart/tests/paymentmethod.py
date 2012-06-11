# -*- coding: utf-8 -*-

from fixture import DataSet
from ticketing.core.models import PaymentMethod
from datetime import datetime

class PaymentMethodData(DataSet):
    class paymentmethod_1:
        name = u'銀行振込'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class paymentmethod_2:
        name = u'クレジットカード'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class paymentmethod_3:
        name = u'コンビニ決済'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
