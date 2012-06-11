# -*- coding: utf-8 -*-

from fixture import DataSet
from ticketing.core.models import Product
from datetime import datetime

class ProductData(DataSet):
    class product_1:
        name = u'シルク・ドゥ・ソレイユ　シアター東京（ZED）A席大人'
        price = 1500
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
