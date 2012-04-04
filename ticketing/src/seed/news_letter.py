# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime

from ticketing.models import *
from ticketing.clients.models import *
from prefecture import PrefectureMaster

class NewsLetterData(DataSet):
    class news_letter_0:
        updated_at      = datetime.now()
        created_at      = datetime.now()

