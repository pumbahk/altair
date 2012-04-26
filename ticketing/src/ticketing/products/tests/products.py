# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.events.models import *
from seed.event import PerformanceData

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

class ProductItemData(DataSet):
    class productitem_1:
        item_type = 1
        product = ProductData.product_1
        performance = PerformanceData.performance_1
        seat_type_id = None
        price_id = None
        status = None
    class productitem_2:
        item_type = 2
        product = ProductData.product_2
        performance = PerformanceData.performance_1
        seat_type_id = None
        price_id = None
        status = None
