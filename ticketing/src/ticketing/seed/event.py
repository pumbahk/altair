# -*- coding: utf-8 -*-

from ticketing.seed import DataSet
from datetime import datetime

from account import AccountData
from organization import OrganizationData

class EventData(DataSet):
    class event_1:
        code = u"RKTZED"
        title = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        abbreviated_title = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        account = AccountData.account_1
        organization = OrganizationData.organization_0
    class event_2:
        code = u"BM2011"
        title = u"ブルーマングループ IN 東京 2011年"
        abbreviated_title = u"ブルーマングループ IN 東京 2011年"
        account = AccountData.account_5
        organization = OrganizationData.organization_0
    class event_3:
        code = u"BM2012"
        title = u"ブルーマングループ IN 東京 2012年"
        abbreviated_title = u"ブルーマングループ IN 東京 2012年"
        account = AccountData.account_5
        organization = OrganizationData.organization_0
    class event_4:
        code = u"DSNICE"
        title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"
        abbreviated_title = u"ディズニー・オン・アイス 「オールスターカーニバル」（名古屋）"
        account = AccountData.account_6
        organization = OrganizationData.organization_0

class PerformanceEvent1Data(DataSet):
    class performance_1:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'201207011800'
        open_on = datetime(2012,7,1,18,0)
        start_on = datetime(2012,7,1,19,0)
        end_on = datetime(2012,7,1,21,0)
        no_period = False
        event = EventData.event_1
        owner = AccountData.account_3
    class performance_2:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'RKTZED070218'
        open_on = datetime(2012,7,2,18,0)
        start_on = datetime(2012,7,2,19,0)
        end_on = datetime(2012,7,2,21,0)
        no_period = False
        event = EventData.event_1
        owner = AccountData.account_3
    class performance_3:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'RKTZED070318'
        open_on = datetime(2012,7,3,18,0)
        start_on = datetime(2012,7,3,19,0)
        end_on = datetime(2012,7,3,21,0)
        no_period = False
        event = EventData.event_1
        owner = AccountData.account_3
    class performance_4:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'RKTZED070418'
        open_on = datetime(2012,7,4,18,0)
        start_on = datetime(2012,7,4,19,0)
        end_on = datetime(2012,7,4,21,0)
        no_period = False
        event = EventData.event_1
        owner = AccountData.account_3
    class performance_5:
        event = EventData.event_1
        name = u"シルク・ドゥ・ソレイユ「ZED （ゼッド）TM」Presented by JCB"
        code = u'RKTZED070518'
        open_on = datetime(2012,7,5,18,0)
        start_on = datetime(2012,7,5,19,0)
        end_on = datetime(2012,7,5,21,0)
        no_period = False
        event = EventData.event_1
        owner = AccountData.account_3

class PerformanceEvent2Data(DataSet):
    class performance_1:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'BM2011070518'
        open_on = datetime(2012,7,5,18,0)
        start_on = datetime(2012,7,5,19,0)
        end_on = datetime(2012,7,5,21,0)
        no_period = False
        event = EventData.event_2
        owner = AccountData.account_4
    class performance_2:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'BM2011070618'
        open_on = datetime(2012,7,6,18,0)
        start_on = datetime(2012,7,6,19,0)
        end_on = datetime(2012,7,6,21,0)
        no_period = False
        event = EventData.event_2
        owner = AccountData.account_4
    class performance_3:
        event = EventData.event_2
        name = u"ブルーマングループ IN 東京 2011年"
        code = u'BM2011070718'
        open_on = datetime(2012,7,7,18,0)
        start_on = datetime(2012,7,7,19,0)
        end_on = datetime(2012,7,7,21,0)
        no_period = False
        event = EventData.event_2
        owner = AccountData.account_4

class SalesSegmentEvent1Data(DataSet):
    class sales_segment_1:
        name = u'先行販売'
        start_at = datetime(2012,5,1,12,0)
        end_at = datetime(2012,7,1,12,0)
        event = EventData.event_1
        upper_limit = 1
        seat_choice = True
    class sales_segment_2:
        name = u'予約販売'
        start_at = datetime(2012,3,1,12,0)
        end_at = datetime(2012,5,1,12,0)
        event = EventData.event_1
        upper_limit = None
        seat_choice = True

class SalesSegmentEvent2Data(DataSet):
    class sales_segment_1:
        name = u'先行販売'
        start_at = datetime(2012,5,1,12,0)
        end_at = datetime(2012,7,1,12,0)
        event = EventData.event_2
        upper_limit = 2
        seat_choice = True
    class sales_segment_2:
        name = u'予約販売'
        start_at = datetime(2012,3,1,12,0)
        end_at = datetime(2012,5,1,12,0)
        event = EventData.event_2
        upper_limit = None
        seat_choice = True
