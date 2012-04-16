# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import PerformanceData
from ticketing.venues.models import SeatMaster, SeatMasterL2, SeatType
from datetime import datetime
from seattype import SeatTypeData
from seatmaster import SeatMasterData

class SeatMasterL2Data(DataSet):
    class seatmasterl2_1:
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seattype_1
        seat = SeatMasterData.seatmaster_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status = 1
    class seatmasterl2_2:
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seattype_2
        seat = SeatMasterData.seatmaster_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status = 1
