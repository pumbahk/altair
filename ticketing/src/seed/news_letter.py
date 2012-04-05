# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.clients.models import *
from prefecture import PrefectureMaster

class NewsLetterData(DataSet):
    class news_letter_1:
        subject          = "hoge"
        description      = "foo"
        start_on         = datetime(2012,7,1,19,0)
        subscriber_count = 1
        status           = "waiting"
        created_at       = datetime.now()
        updated_at       = datetime.now()
    class news_letter_2:
        subject          = "hoge2"
        description      = "foo2"
        start_on         = datetime(2012,8,1,19,0)
        subscriber_count = 2
        status           = "complete"
        created_at       = datetime.now()
        updated_at       = datetime.now()

