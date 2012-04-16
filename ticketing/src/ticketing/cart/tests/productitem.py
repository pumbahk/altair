# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import PerformanceData
from ticketing.products.models import ProductItem
from datetime import datetime
from product import ProductData
from price import PriceData
from seattype import SeatTypeData

class ProductItemData(DataSet):
    class productitem_1:
        product = ProductData.product_1
        performance = PerformanceData.performance_1
        price = PriceData.price_1
        seat_type = SeatTypeData.seattype_1
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
