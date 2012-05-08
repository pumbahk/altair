# -*- coding: utf-8 -*-

from datetime import datetime
from ticketing.seed import DataSet

from account import AccountData
from event import PerformanceData, EventData
from organization import OrganizationData
from venue import SeatTypeData

class SalesSegmentData(DataSet):
    class sales_segment_1:
        name = u'先行販売'
        start_at = datetime(2012,5,1,12,0)
        end_at = datetime(2012,7,1,12,0)
        organization = OrganizationData.organization_0
    class sales_segment_2:
        name = u'予約販売'
        start_at = datetime(2012,3,1,12,0)
        end_at = datetime(2012,5,1,12,0)
        organization = OrganizationData.organization_0

class ProductData(DataSet):
    class product_1:
        name = u"S席大人"
        price = 8000
        status = None
        sales_segment = SalesSegmentData.sales_segment_1
        event = EventData.event_1
    class product_2:
        name = u"S席子供"
        price = 4000
        status = None
        sales_segment = SalesSegmentData.sales_segment_1
        event = EventData.event_1
    class product_3:
        name = u"A席大人"
        price = 7000
        status = None
        sales_segment = SalesSegmentData.sales_segment_1
        event = EventData.event_1
    class product_4:
        name = u"A席子供"
        price = 3000
        status = None
        sales_segment = SalesSegmentData.sales_segment_2
        event = EventData.event_1
    class product_5:
        name = u"S席大人+駐車場券"
        price = 8000
        status = None
        sales_segment = SalesSegmentData.sales_segment_2
        event = EventData.event_1

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

class StockHolderData(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceData.performance_1
        account = AccountData.account_1
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceData.performance_1
        account = AccountData.account_1
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceData.performance_1
        account = AccountData.account_1
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceData.performance_1
        account = AccountData.account_1
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceData.performance_1
        account = AccountData.account_2
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceData.performance_1
        account = AccountData.account_3

class StockData(DataSet):
    class stock_1:
        quantity = 1000
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_1
        stock_holder = StockHolderData.stock_holder_1
    class stock_2:
        quantity = 800
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_2
        stock_holder = StockHolderData.stock_holder_1
    class stock_3:
        quantity = 500
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_3
        stock_holder = StockHolderData.stock_holder_1
    class stock_4:
        quantity = 0
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_4
        stock_holder = StockHolderData.stock_holder_1
    class stock_5:
        quantity = 60
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_1
        stock_holder = StockHolderData.stock_holder_5
    class stock_6:
        quantity = 50
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_2
        stock_holder = StockHolderData.stock_holder_5
    class stock_7:
        quantity = 40
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_3
        stock_holder = StockHolderData.stock_holder_5
    class stock_8:
        quantity = 30
        performance = PerformanceData.performance_1
        seat_type = SeatTypeData.seat_type_4
        stock_holder = StockHolderData.stock_holder_5
