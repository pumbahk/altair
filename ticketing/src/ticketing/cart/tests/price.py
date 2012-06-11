# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import EventData
from ticketing.core.models import Price
from datetime import datetime

class PriceData(DataSet):
    class price_1:
        name = u'A席大人'
        event = EventData.event_0
        price = 1500
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class price_2:
        name = u'A席子供'
        event = EventData.event_0
        price = 1000
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
