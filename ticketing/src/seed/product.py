# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from event import PerformanceData

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
