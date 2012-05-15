# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import PerformanceData
from ticketing.venues.models import SeatMaster, SeatMasterL2, StockType
from datetime import datetime
from stocktype import StockTypeData
from seatmaster import SeatMasterData

class SeatMasterL2Data(DataSet):
    class seatmasterl2_1:
        performance = PerformanceData.performance_1
        stock_type = StockTypeData.stocktype_1
        seat = SeatMasterData.seatmaster_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status = 1
    class seatmasterl2_2:
        performance = PerformanceData.performance_1
        stock_type = StockTypeData.stocktype_2
        seat = SeatMasterData.seatmaster_2
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status = 1
