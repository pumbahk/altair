# -*- coding: utf-8 -*-

from fixture import DataSet
from datetime import datetime

#from seed.client import ClientData

class BookmarkData(DataSet):

    class bookmark_1:
        name = u"Google Analytics"
        url = u"http://example.com"
#        client        = ClientData.client_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class bookmark_2:
        name = u"Google Adwords"
        url = u"http://example.com"
#        client        = ClientData.client_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
    class bookmark_3:
        name = u"Ginzametrics"
        url = u"http://example.com"
#        client        = ClientData.client_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1

    class bookmark_4:
        name = u"Desk.com"
        url = u"http://example.com"
#        client        = ClientData.client_0
        updated_at      = datetime.now()
        created_at      = datetime.now()
        status          = 1
