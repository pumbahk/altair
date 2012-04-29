# -*- coding: utf-8 -*-

from seed import DataSet

from seed.event import PerformanceData
from seed.venue import SeatTypeData

class ProductData(DataSet):
    class product_1:
        name = u"S席大人"
        price = 8000
        status = None
    class product_2:
        name = u"S席子供"
        price = 4000
        status = None
    class product_3:
        name = u"A席大人"
        price = 7000
        status = None
    class product_4:
        name = u"A席子供"
        price = 3000
        status = None
    class product_5:
        name = u"S席大人+駐車場券"
        price = 8000
        status = None

class ProductItemData(DataSet):
    class productitem_1:
        item_type = 1
        product = ProductData.product_1
        performance = PerformanceData.performance_1
        status = None
    class productitem_2:
        item_type = 2
        product = ProductData.product_2
        performance = PerformanceData.performance_1
        status = None
    class productitem_3:
        item_type = 1
        product = ProductData.product_1
        performance = PerformanceData.performance_1
        status = None

class StockData(DataSet):
    class stock_1:
        quantity = 1000
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_1
    class stock_2:
        quantity = 800
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_2
    class stock_3:
        quantity = 500
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_3
    class stock_4:
        quantity = 0
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_4
