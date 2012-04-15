# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import EventData
from ticketing.venues.models import SeatType
from datetime import datetime

class SeatTypeData(DataSet):
    class seattype_1:
        name = u'A席'
        event = EventData.event_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class seattype_2:
        name = u'B席'
        event = EventData.event_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
