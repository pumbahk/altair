# -*- coding: utf-8 -*-

from datetime import datetime
from ticketing.seed import DataSet

from account import AccountData
from .event import PerformanceData, EventData
from .organization import OrganizationData

class SeatTypeData(DataSet):
    class seat_type_1:
        name = u'S席'
        performance_id = 1
        style = {"text": "S", "stroke": {"color": "#000000", "width": "1", "pattern": "solid"}, "fill": {"color": "#d8d8d8"}}
        status = 1
    class seat_type_2:
        name = u'A席'
        performance_id = 1
        style = {"text": "A", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "solid"}, "fill": {"color": "#ffec9f"}}
        status = 1
    class seat_type_3:
        name = u'B席'
        performance_id = 1
        style = {"text": "B", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "double"}, "fill": {"color": "#99b3e6"}}
        status = 1
    class seat_type_4:
        name = u'C席'
        performance_id = 1
        style = {"text": "C", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "dotted"}, "fill": {"color": "#cc8080"}}
        status = 1

class SalesSegmentData(DataSet):
    class sales_segment_1:
        name = u'先行販売'
        start_at = datetime(2012,5,1,12,0)
        end_at = datetime(2012,7,1,12,0)
        performance = PerformanceData.performance_1
        organization = OrganizationData.organization_0
    class sales_segment_2:
        name = u'予約販売'
        start_at = datetime(2012,3,1,12,0)
        end_at = datetime(2012,5,1,12,0)
        performance = PerformanceData.performance_1
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
        price = 9000
        status = None
        sales_segment = SalesSegmentData.sales_segment_2
        event = EventData.event_1

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
        quantity = 5
        seat_type = SeatTypeData.seat_type_1
        stock_holder = StockHolderData.stock_holder_1
    class stock_2:
        quantity = 3
        seat_type = SeatTypeData.seat_type_2
        stock_holder = StockHolderData.stock_holder_1
    class stock_3:
        quantity = 2
        seat_type = SeatTypeData.seat_type_3
        stock_holder = StockHolderData.stock_holder_1
    class stock_4:
        quantity = 3
        seat_type = SeatTypeData.seat_type_4
        stock_holder = StockHolderData.stock_holder_1
    class stock_5:
        quantity = 4
        seat_type = SeatTypeData.seat_type_1
        stock_holder = StockHolderData.stock_holder_5
    class stock_6:
        quantity = 4
        seat_type = SeatTypeData.seat_type_2
        stock_holder = StockHolderData.stock_holder_5
    class stock_7:
        quantity = 3
        seat_type = SeatTypeData.seat_type_3
        stock_holder = StockHolderData.stock_holder_5
    class stock_8:
        quantity = 3
        seat_type = SeatTypeData.seat_type_4
        stock_holder = StockHolderData.stock_holder_5

class ProductItemData(DataSet):
    class productitem_1:
        item_type = 1
        price = 8000
        product = ProductData.product_1
        performance = PerformanceData.performance_1
        stock = StockData.stock_1
        seat_type = SeatTypeData.seat_type_1
        status = None
    class productitem_2:
        item_type = 2
        price = 4000
        product = ProductData.product_2
        performance = PerformanceData.performance_1
        stock = StockData.stock_2
        seat_type = SeatTypeData.seat_type_2
        status = None
    class productitem_3:
        item_type = 1
        price = 7000
        product = ProductData.product_3
        performance = PerformanceData.performance_1
        stock = StockData.stock_3
        seat_type = SeatTypeData.seat_type_3
        status = None
    class productitem_4:
        item_type = 1
        price = 3000
        product = ProductData.product_4
        performance = PerformanceData.performance_1
        stock = StockData.stock_4
        seat_type = SeatTypeData.seat_type_4
        status = None
    class productitem_5:
        item_type = 1
        price = 8000
        product = ProductData.product_5
        performance = PerformanceData.performance_1
        stock = StockData.stock_5
        seat_type = SeatTypeData.seat_type_1
        status = None
