# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.clients.models import *
from prefecture import PrefectureMaster

class NewsletterData(DataSet):
    class newsletter_1:
        subject          = "「ブラスト！2012」全国ツアー／「ツタンカーメン展」情報満載！ 【楽天チケットニュース】"
        description      = "foo ${name} bar ${name}"
        type             = "html"
        status           = "waiting"
        subscriber_count = 1
        start_on         = datetime(2012,4,1,19,0)
        created_at       = datetime.now()
        updated_at       = datetime.now()
    class newsletter_2:
        subject          = "hoge2"
        description      = "foo ${name} bar ${name}"
        type             = "text"
        status           = "completed"
        subscriber_count = 2
        start_on         = datetime(2012,8,1,19,0)
        created_at       = datetime.now()
        updated_at       = datetime.now()

