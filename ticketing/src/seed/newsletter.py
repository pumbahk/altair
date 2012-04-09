# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.clients.models import *
from prefecture import PrefectureMaster

class NewsletterData(DataSet):
    class newsletter_1:
        subject          = "hoge"
        description      = "foo"
        start_on         = datetime(2012,4,1,19,0)
        subscriber_count = 1
        status           = "waiting"
        created_at       = datetime.now()
        updated_at       = datetime.now()
    class newsletter_2:
        subject          = "hoge2"
        description      = "foo2"
        start_on         = datetime(2012,8,1,19,0)
        subscriber_count = 2
        status           = "completed"
        created_at       = datetime.now()
        updated_at       = datetime.now()

