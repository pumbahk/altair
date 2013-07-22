# -*- coding: utf-8 -*-

from fixture import DataSet
from altair.app.ticketing.core.models import SalesSegment
from datetime import datetime

class SalesSegmentData(DataSet):
    class salessegment_1:
        name = u'ネット販売・郵送'
        start_at = datetime(2012,7,15,0,0)
        end_at = datetime(2012,7,30,23,59)
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
