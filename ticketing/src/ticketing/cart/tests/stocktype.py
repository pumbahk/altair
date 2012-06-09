# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import EventData
from ticketing.core.models import StockType
from datetime import datetime

class StockTypeData(DataSet):
    class stocktype_1:
        name = u'A席'
        event = EventData.event_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class stocktype_2:
        name = u'B席'
        event = EventData.event_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
