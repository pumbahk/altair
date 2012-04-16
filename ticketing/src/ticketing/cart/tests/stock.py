# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import PerformanceData
from ticketing.products.models import Stock
from datetime import datetime
from stockholder import StockHolderData
from seattype import SeatTypeData

class StockData(DataSet):
    class stock_1:
        performance = PerformanceData.performance_1
        stock_holder = StockHolderData.stockholder_1
        seat_type = SeatTypeData.seattype_1
        quantity = 1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
