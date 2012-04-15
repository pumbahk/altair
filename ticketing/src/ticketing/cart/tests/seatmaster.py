# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import EventData
from seed.venue import VenueData
from ticketing.venues.models import SeatMaster
from datetime import datetime

class SeatMasterData(DataSet):
    class seatmaster_1:
        identifieir = u'001'
        venue = VenueData.venue_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class seatmaster_2:
        identifieir = u'002'
        venue = VenueData.venue_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
