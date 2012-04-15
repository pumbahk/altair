# -*- coding: utf-8 -*-

from fixture import DataSet
from seed.event import EventData
from ticketing.products.models import SalesSegmentSet
from datetime import datetime
from product import ProductData

class SalesSegmentSetData(DataSet):
    class salessegmentset_1:
        product = ProductData.product_1
        event = EventData.event_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
