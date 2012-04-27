# -*- coding: utf-8 -*-

from seed import DataSet
from datetime import datetime
from account import AccountData
from venue import VenueData

from ticketing.models import *
from ticketing.organizations.models import *
from prefecture import PrefectureMaster

class EventData(DataSet):
    class event_1:
        code = u"ZED"
        title = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        abbreviated_title = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        start_on = datetime(2012,7,1,19,0)
        end_on = datetime(2012,9,30,19,0)
    class event_2:
        code = u"BLUEMAN2011"
        title = u"ブルーマングループ IN 東京 2011年"
        abbreviated_title = u"ブルーマングループ IN 東京 2011年"
        start_on = datetime(2012,8,1,19,0)
        end_on = datetime(2012,10,30,19,0)
    class event_3:
        code = u"BLUEMAN2012"
        title = u"ブルーマングループ IN 東京 2012年"
        abbreviated_title = u"ブルーマングループ IN 東京 2012年"
        start_on = datetime(2012,9,1,19,0)
        end_on = datetime(2012,11,30,19,0)
    class event_4:
        code = u"DISNEYICE"
        title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"
        abbreviated_title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"
        start_on = datetime(2012,9,1,19,0)
        end_on = datetime(2012,10,30,19,0)

class PerformanceData(DataSet):
    class performance_1:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,1,18,0)
        start_on = datetime(2012,7,1,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_2:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,2,18,0)
        start_on = datetime(2012,7,2,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_3:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,3,18,0)
        start_on = datetime(2012,7,3,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_4:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,4,18,0)
        start_on = datetime(2012,7,4,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_5:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,5,18,0)
        start_on = datetime(2012,7,5,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_2
        venue = VenueData.venue_1
    class performance_6:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'201207011800'
        open_on = datetime(2012,7,5,18,0)
        start_on = datetime(2012,7,5,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_3
        venue = VenueData.venue_2
    class performance_7:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'201207011800'
        open_on = datetime(2012,7,6,18,0)
        start_on = datetime(2012,7,6,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_3
        venue = VenueData.venue_2
    class performance_8:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'201207011800'
        open_on = datetime(2012,7,7,18,0)
        start_on = datetime(2012,7,7,19,0)
        end_on = None
        no_period = False
        owner = AccountData.account_3
        venue = VenueData.venue_2
