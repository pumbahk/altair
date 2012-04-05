# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime
from account import AccountData
from venue import VenueData

from ticketing.models import *
from ticketing.clients.models import *
from prefecture import PrefectureMaster

class EventData(DataSet):
    class event_0:
        start_on = None
        end_on = None
        code = u"ZED"
        title =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        abbreviated_title = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
    class event_1:
        start_on = None
        end_on = None
        code = u"BLUEMAN2011"
        title = u"ブルーマングループ IN 東京 2011年"
        abbreviated_title = u"ブルーマングループ IN 東京 2011年"
    class event_2:
        start_on = None
        end_on = None
        code = u"BLUEMAN2012"
        title = u"ブルーマングループ IN 東京 2012年"
        abbreviated_title = u"ブルーマングループ IN 東京 2012年"
    class event_3:
        start_on = None
        end_on = None
        code = u"DISNEYICE"
        title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"
        abbreviated_title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"


class PerformanceData(DataSet):
    class performance_1:
        event = EventData.event_0
        start_on = datetime(2012,7,1,19,0)
        end_on = None
        open_on = datetime(2012,7,1,18,0)
        no_period = False
        name =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_2:
        event = EventData.event_0
        start_on = datetime(2012,7,2,19,0)
        end_on = None
        open_on = datetime(2012,7,2,18,0)
        no_period = False
        name =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_3:
        event = EventData.event_0
        start_on = datetime(2012,7,3,19,0)
        end_on = None
        open_on = datetime(2012,7,3,18,0)
        no_period = False
        name =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_4:
        event = EventData.event_0
        start_on = datetime(2012,7,4,19,0)
        end_on = None
        open_on = datetime(2012,7,4,18,0)
        no_period = False
        name =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_5:
        event = EventData.event_0
        start_on = datetime(2012,7,5,19,0)
        end_on = None
        open_on = datetime(2012,7,5,18,0)
        no_period = False
        name =  u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        owner = AccountData.account_2
        venue = VenueData.venue_1