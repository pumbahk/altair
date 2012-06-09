# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import PerformanceData
from ticketing.core.models import SeatStock, SeatStatusEnum
from datetime import datetime
from stock import StockData
from seatmasterl2 import SeatMasterL2Data

class SeatStockData(DataSet):
    class seatstock_1:
        stock = StockData.stock_1
        seat = SeatMasterL2Data.seatmasterl2_1
        sold = False
        status = SeatStatusEnum.Vacant.v
        updated_at      = datetime.now()
        created_at      = datetime.now()
    class seatstock_2:
        stock = StockData.stock_1
        seat = SeatMasterL2Data.seatmasterl2_2
        sold = False
        status = SeatStatusEnum.InCart.v
        updated_at      = datetime.now()
        created_at      = datetime.now()
