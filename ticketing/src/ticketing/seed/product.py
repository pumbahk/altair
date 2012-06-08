# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from ticketing.products.models import *

from account import AccountData
from .event import EventData, SalesSegmentEvent1Data, SalesSegmentEvent2Data, PerformanceEvent1Data, PerformanceEvent2Data

class StockTypeEvent1Data(DataSet):
    class stock_type_1:
        name = u'S席'
        event = EventData.event_1
        style = {"text": "", "stroke": {"color": "#000000", "width": "1", "pattern": "solid"}, "fill": {"color": "#d8d8d8"}}
        type = StockTypeEnum.Seat.v
    class stock_type_2:
        name = u'A席'
        event = EventData.event_1
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "solid"}, "fill": {"color": "#ffec9f"}}
        type = StockTypeEnum.Seat.v
    class stock_type_3:
        name = u'B席'
        event = EventData.event_1
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "double"}, "fill": {"color": "#99b3e6"}}
        type = StockTypeEnum.Seat.v
    class stock_type_4:
        name = u'C席'
        event = EventData.event_1
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "dotted"}, "fill": {"color": "#cc8080"}}
        type = StockTypeEnum.Seat.v

class StockTypeEvent2Data(DataSet):
    class stock_type_1:
        name = u'S席'
        event = EventData.event_2
        style = {"text": "", "stroke": {"color": "#000000", "width": "1", "pattern": "solid"}, "fill": {"color": "#d8d8d8"}}
        type = StockTypeEnum.Seat.v
    class stock_type_2:
        name = u'A席'
        event = EventData.event_2
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "solid"}, "fill": {"color": "#ffec9f"}}
        type = StockTypeEnum.Seat.v
    class stock_type_3:
        name = u'B席'
        event = EventData.event_2
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "double"}, "fill": {"color": "#99b3e6"}}
        type = StockTypeEnum.Seat.v
    class stock_type_4:
        name = u'C席'
        event = EventData.event_2
        style = {"text": "", "stroke": {"color": "#d8d8d8", "width": "1", "pattern": "dotted"}, "fill": {"color": "#cc8080"}}
        type = StockTypeEnum.Seat.v

class ProductEvent1Data(DataSet):
    class product_1:
        name = u"S席大人"
        price = 8000
        status = None
        sales_segment = SalesSegmentEvent1Data.sales_segment_1
        event = EventData.event_1
    class product_2:
        name = u"S席子供"
        price = 4000
        status = None
        sales_segment = SalesSegmentEvent1Data.sales_segment_1
        event = EventData.event_1
    class product_3:
        name = u"A席大人"
        price = 7000
        status = None
        sales_segment = SalesSegmentEvent1Data.sales_segment_1
        event = EventData.event_1
    class product_4:
        name = u"A席子供"
        price = 3000
        status = None
        sales_segment = SalesSegmentEvent1Data.sales_segment_2
        event = EventData.event_1
    class product_5:
        name = u"S席大人+駐車場券"
        price = 9000
        status = None
        sales_segment = SalesSegmentEvent1Data.sales_segment_2
        event = EventData.event_1

class ProductEvent2Data(DataSet):
    class product_1:
        name = u"S席大人"
        price = 8000
        status = None
        sales_segment = SalesSegmentEvent2Data.sales_segment_1
        event = EventData.event_2
    class product_2:
        name = u"S席子供"
        price = 4000
        status = None
        sales_segment = SalesSegmentEvent2Data.sales_segment_1
        event = EventData.event_2
    class product_3:
        name = u"A席大人"
        price = 7000
        status = None
        sales_segment = SalesSegmentEvent2Data.sales_segment_1
        event = EventData.event_2
    class product_4:
        name = u"A席子供"
        price = 3000
        status = None
        sales_segment = SalesSegmentEvent2Data.sales_segment_2
        event = EventData.event_2
    class product_5:
        name = u"S席大人+駐車場券"
        price = 9000
        status = None
        sales_segment = SalesSegmentEvent2Data.sales_segment_2
        event = EventData.event_2

class StockHolderEvent1Performance1Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent1Data.performance_1
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent1Performance2Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent1Data.performance_2
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent1Performance3Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent1Data.performance_3
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent1Performance4Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent1Data.performance_4
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent1Performance5Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent1Data.performance_5
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent2Performance1Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent2Data.performance_1
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent2Performance2Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent2Data.performance_2
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockHolderEvent2Performance3Data(DataSet):
    class stock_holder_1:
        name = u'招待枠'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_1
        style = {"text": "招", "text_color": "#d9ccbf"}
    class stock_holder_2:
        name = u'事故席枠'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_1
        style = {"text": "事", "text_color": "#d9ccbf"}
    class stock_holder_3:
        name = u'ネット販売'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_1
        style = {"text": "ネ", "text_color": "#d9ccbf"}
    class stock_holder_4:
        name = u'一般販売'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_1
        style = {"text": "一", "text_color": "#d9ccbf"}
    class stock_holder_5:
        name = u'ぴあ配券'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_2
        style = {"text": "ぴ", "text_color": "#d9ccbf"}
    class stock_holder_6:
        name = u'イープラス配券'
        performance = PerformanceEvent2Data.performance_3
        account = AccountData.account_3
        style = {"text": "e", "text_color": "#d9ccbf"}

class StockEvent1Performance1Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent1Data.performance_1
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance1Data.stock_holder_5

class StockEvent1Performance2Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent1Data.performance_2
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance2Data.stock_holder_5

class StockEvent1Performance3Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent1Data.performance_3
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance3Data.stock_holder_5

class StockEvent1Performance4Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent1Data.performance_4
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance4Data.stock_holder_5

class StockEvent1Performance5Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_1
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_2
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_3
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent1Data.performance_5
        stock_type = StockTypeEvent1Data.stock_type_4
        stock_holder = StockHolderEvent1Performance5Data.stock_holder_5

class StockEvent2Performance1Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent2Data.performance_1
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance1Data.stock_holder_5

class StockEvent2Performance2Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent2Data.performance_2
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance2Data.stock_holder_5

class StockEvent2Performance3Data(DataSet):
    class stock_1:
        quantity = 6
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_1
    class stock_2:
        quantity = 3
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_1
    class stock_3:
        quantity = 2
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_1
    class stock_4:
        quantity = 3
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_1
    class stock_5:
        quantity = 3
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_1
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_5
    class stock_6:
        quantity = 4
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_2
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_5
    class stock_7:
        quantity = 3
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_3
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_5
    class stock_8:
        quantity = 3
        performance = PerformanceEvent2Data.performance_3
        stock_type = StockTypeEvent2Data.stock_type_4
        stock_holder = StockHolderEvent2Performance3Data.stock_holder_5

class StockStatusEvent1Performance1Data(DataSet):
    class stock_status_1:
        stock = StockEvent1Performance1Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent1Performance1Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent1Performance1Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent1Performance1Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent1Performance1Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent1Performance1Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent1Performance1Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent1Performance1Data.stock_8
        quantity = 3

class StockStatusEvent1Performance2Data(DataSet):
    class stock_status_1:
        stock = StockEvent1Performance2Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent1Performance2Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent1Performance2Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent1Performance2Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent1Performance2Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent1Performance2Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent1Performance2Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent1Performance2Data.stock_8
        quantity = 3

class StockStatusEvent1Performance3Data(DataSet):
    class stock_status_1:
        stock = StockEvent1Performance3Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent1Performance3Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent1Performance3Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent1Performance3Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent1Performance3Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent1Performance3Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent1Performance3Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent1Performance3Data.stock_8
        quantity = 3

class StockStatusEvent1Performance4Data(DataSet):
    class stock_status_1:
        stock = StockEvent1Performance4Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent1Performance4Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent1Performance4Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent1Performance4Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent1Performance4Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent1Performance4Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent1Performance4Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent1Performance4Data.stock_8
        quantity = 3

class StockStatusEvent1Performance5Data(DataSet):
    class stock_status_1:
        stock = StockEvent1Performance5Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent1Performance5Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent1Performance5Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent1Performance5Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent1Performance5Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent1Performance5Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent1Performance5Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent1Performance5Data.stock_8
        quantity = 3

class StockStatusEvent2Performance1Data(DataSet):
    class stock_status_1:
        stock = StockEvent2Performance1Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent2Performance1Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent2Performance1Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent2Performance1Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent2Performance1Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent2Performance1Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent2Performance1Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent2Performance1Data.stock_8
        quantity = 3

class StockStatusEvent2Performance2Data(DataSet):
    class stock_status_1:
        stock = StockEvent2Performance2Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent2Performance2Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent2Performance2Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent2Performance2Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent2Performance2Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent2Performance2Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent2Performance2Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent2Performance2Data.stock_8
        quantity = 3

class StockStatusEvent2Performance3Data(DataSet):
    class stock_status_1:
        stock = StockEvent2Performance3Data.stock_1
        quantity = 1
    class stock_status_2:
        stock = StockEvent2Performance3Data.stock_2
        quantity = 3
    class stock_status_3:
        stock = StockEvent2Performance3Data.stock_3
        quantity = 2
    class stock_status_4:
        stock = StockEvent2Performance3Data.stock_4
        quantity = 3
    class stock_status_5:
        stock = StockEvent2Performance3Data.stock_5
        quantity = 3
    class stock_status_6:
        stock = StockEvent2Performance3Data.stock_6
        quantity = 4
    class stock_status_7:
        stock = StockEvent2Performance3Data.stock_7
        quantity = 3
    class stock_status_8:
        stock = StockEvent2Performance3Data.stock_8
        quantity = 3

class StockAllocationEvent1Performance1Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent1Data.stock_type_1
        performance = PerformanceEvent1Data.performance_1
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent1Data.stock_type_2
        performance = PerformanceEvent1Data.performance_1
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent1Data.stock_type_3
        performance = PerformanceEvent1Data.performance_1
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent1Data.stock_type_4
        performance = PerformanceEvent1Data.performance_1
        quantity = 6

class StockAllocationEvent1Performance2Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent1Data.stock_type_1
        performance = PerformanceEvent1Data.performance_2
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent1Data.stock_type_2
        performance = PerformanceEvent1Data.performance_2
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent1Data.stock_type_3
        performance = PerformanceEvent1Data.performance_2
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent1Data.stock_type_4
        performance = PerformanceEvent1Data.performance_2
        quantity = 6

class StockAllocationEvent1Performance3Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent1Data.stock_type_1
        performance = PerformanceEvent1Data.performance_3
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent1Data.stock_type_2
        performance = PerformanceEvent1Data.performance_3
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent1Data.stock_type_3
        performance = PerformanceEvent1Data.performance_3
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent1Data.stock_type_4
        performance = PerformanceEvent1Data.performance_3
        quantity = 6

class StockAllocationEvent1Performance4Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent1Data.stock_type_1
        performance = PerformanceEvent1Data.performance_4
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent1Data.stock_type_2
        performance = PerformanceEvent1Data.performance_4
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent1Data.stock_type_3
        performance = PerformanceEvent1Data.performance_4
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent1Data.stock_type_4
        performance = PerformanceEvent1Data.performance_4
        quantity = 6

class StockAllocationEvent1Performance5Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent1Data.stock_type_1
        performance = PerformanceEvent1Data.performance_5
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent1Data.stock_type_2
        performance = PerformanceEvent1Data.performance_5
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent1Data.stock_type_3
        performance = PerformanceEvent1Data.performance_5
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent1Data.stock_type_4
        performance = PerformanceEvent1Data.performance_5
        quantity = 6

class StockAllocationEvent2Performance1Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent2Data.stock_type_1
        performance = PerformanceEvent2Data.performance_1
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent2Data.stock_type_2
        performance = PerformanceEvent2Data.performance_1
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent2Data.stock_type_3
        performance = PerformanceEvent2Data.performance_1
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent2Data.stock_type_4
        performance = PerformanceEvent2Data.performance_1
        quantity = 6

class StockAllocationEvent2Performance2Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent2Data.stock_type_1
        performance = PerformanceEvent2Data.performance_2
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent2Data.stock_type_2
        performance = PerformanceEvent2Data.performance_2
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent2Data.stock_type_3
        performance = PerformanceEvent2Data.performance_2
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent2Data.stock_type_4
        performance = PerformanceEvent2Data.performance_2
        quantity = 6

class StockAllocationEvent2Performance3Data(DataSet):
    class stock_allocation_1:
        stock_type = StockTypeEvent2Data.stock_type_1
        performance = PerformanceEvent2Data.performance_3
        quantity = 9
    class stock_allocation_2:
        stock_type = StockTypeEvent2Data.stock_type_2
        performance = PerformanceEvent2Data.performance_3
        quantity = 7
    class stock_allocation_3:
        stock_type = StockTypeEvent2Data.stock_type_3
        performance = PerformanceEvent2Data.performance_3
        quantity = 5
    class stock_allocation_4:
        stock_type = StockTypeEvent2Data.stock_type_4
        performance = PerformanceEvent2Data.performance_3
        quantity = 6

class ProductItemEvent1Performance1Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_1
        performance = PerformanceEvent1Data.performance_1
        stock = StockEvent1Performance1Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent1Data.product_2
        performance = PerformanceEvent1Data.performance_1
        stock = StockEvent1Performance1Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent1Data.product_3
        performance = PerformanceEvent1Data.performance_1
        stock = StockEvent1Performance1Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent1Data.product_4
        performance = PerformanceEvent1Data.performance_1
        stock = StockEvent1Performance1Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_5
        performance = PerformanceEvent1Data.performance_1
        stock = StockEvent1Performance1Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1

class ProductItemEvent1Performance2Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_1
        performance = PerformanceEvent1Data.performance_2
        stock = StockEvent1Performance2Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent1Data.product_2
        performance = PerformanceEvent1Data.performance_2
        stock = StockEvent1Performance2Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent1Data.product_3
        performance = PerformanceEvent1Data.performance_2
        stock = StockEvent1Performance2Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent1Data.product_4
        performance = PerformanceEvent1Data.performance_2
        stock = StockEvent1Performance2Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_5
        performance = PerformanceEvent1Data.performance_2
        stock = StockEvent1Performance2Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1

class ProductItemEvent1Performance3Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_1
        performance = PerformanceEvent1Data.performance_3
        stock = StockEvent1Performance3Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent1Data.product_2
        performance = PerformanceEvent1Data.performance_3
        stock = StockEvent1Performance3Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent1Data.product_3
        performance = PerformanceEvent1Data.performance_3
        stock = StockEvent1Performance3Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent1Data.product_4
        performance = PerformanceEvent1Data.performance_3
        stock = StockEvent1Performance3Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_5
        performance = PerformanceEvent1Data.performance_3
        stock = StockEvent1Performance3Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1

class ProductItemEvent1Performance4Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_1
        performance = PerformanceEvent1Data.performance_4
        stock = StockEvent1Performance4Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent1Data.product_2
        performance = PerformanceEvent1Data.performance_4
        stock = StockEvent1Performance4Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent1Data.product_3
        performance = PerformanceEvent1Data.performance_4
        stock = StockEvent1Performance4Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent1Data.product_4
        performance = PerformanceEvent1Data.performance_4
        stock = StockEvent1Performance4Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_5
        performance = PerformanceEvent1Data.performance_4
        stock = StockEvent1Performance4Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1

class ProductItemEvent1Performance5Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_1
        performance = PerformanceEvent1Data.performance_5
        stock = StockEvent1Performance5Data.stock_1
        stock_type = StockTypeEvent1Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent1Data.product_2
        performance = PerformanceEvent1Data.performance_5
        stock = StockEvent1Performance5Data.stock_2
        stock_type = StockTypeEvent1Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent1Data.product_3
        performance = PerformanceEvent1Data.performance_5
        stock = StockEvent1Performance5Data.stock_3
        stock_type = StockTypeEvent1Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent1Data.product_4
        performance = PerformanceEvent1Data.performance_5
        stock = StockEvent1Performance5Data.stock_4
        stock_type = StockTypeEvent1Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent1Data.product_5
        performance = PerformanceEvent1Data.performance_5
        stock = StockEvent1Performance5Data.stock_5
        stock_type = StockTypeEvent1Data.stock_type_1

class ProductItemEvent2Performance1Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_1
        performance = PerformanceEvent2Data.performance_1
        stock = StockEvent2Performance1Data.stock_1
        stock_type = StockTypeEvent2Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent2Data.product_2
        performance = PerformanceEvent2Data.performance_1
        stock = StockEvent2Performance1Data.stock_2
        stock_type = StockTypeEvent2Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent2Data.product_3
        performance = PerformanceEvent2Data.performance_1
        stock = StockEvent2Performance1Data.stock_3
        stock_type = StockTypeEvent2Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent2Data.product_4
        performance = PerformanceEvent2Data.performance_1
        stock = StockEvent2Performance1Data.stock_4
        stock_type = StockTypeEvent2Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_5
        performance = PerformanceEvent2Data.performance_1
        stock = StockEvent2Performance1Data.stock_5
        stock_type = StockTypeEvent2Data.stock_type_1

class ProductItemEvent2Performance2Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_1
        performance = PerformanceEvent2Data.performance_2
        stock = StockEvent2Performance2Data.stock_1
        stock_type = StockTypeEvent2Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent2Data.product_2
        performance = PerformanceEvent2Data.performance_2
        stock = StockEvent2Performance2Data.stock_2
        stock_type = StockTypeEvent2Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent2Data.product_3
        performance = PerformanceEvent2Data.performance_2
        stock = StockEvent2Performance2Data.stock_3
        stock_type = StockTypeEvent2Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent2Data.product_4
        performance = PerformanceEvent2Data.performance_2
        stock = StockEvent2Performance2Data.stock_4
        stock_type = StockTypeEvent2Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_5
        performance = PerformanceEvent2Data.performance_2
        stock = StockEvent2Performance2Data.stock_5
        stock_type = StockTypeEvent2Data.stock_type_1

class ProductItemEvent2Performance3Data(DataSet):
    class productitem_1:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_1
        performance = PerformanceEvent2Data.performance_3
        stock = StockEvent2Performance3Data.stock_1
        stock_type = StockTypeEvent2Data.stock_type_1
    class productitem_2:
        quantity = 1
        item_type = 2
        price = 4000
        product = ProductEvent2Data.product_2
        performance = PerformanceEvent2Data.performance_3
        stock = StockEvent2Performance3Data.stock_2
        stock_type = StockTypeEvent2Data.stock_type_2
    class productitem_3:
        quantity = 1
        item_type = 1
        price = 7000
        product = ProductEvent2Data.product_3
        performance = PerformanceEvent2Data.performance_3
        stock = StockEvent2Performance3Data.stock_3
        stock_type = StockTypeEvent2Data.stock_type_3
    class productitem_4:
        quantity = 1
        item_type = 1
        price = 3000
        product = ProductEvent2Data.product_4
        performance = PerformanceEvent2Data.performance_3
        stock = StockEvent2Performance3Data.stock_4
        stock_type = StockTypeEvent2Data.stock_type_4
    class productitem_5:
        quantity = 1
        item_type = 1
        price = 8000
        product = ProductEvent2Data.product_5
        performance = PerformanceEvent2Data.performance_3
        stock = StockEvent2Performance3Data.stock_5
        stock_type = StockTypeEvent2Data.stock_type_1

