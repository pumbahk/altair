# -*- coding: utf-8 -*-

from fixture import DataSet
from ticketing.core.models import DeliveryMethod
from datetime import datetime

class DeliveryMethodData(DataSet):
    class deliverymethod_1:
        name = u'郵送'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class deliverymethod_2:
        name = u'コンビニ受取'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class deliverymethod_3:
        name = u'窓口'
        fee = 5
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
