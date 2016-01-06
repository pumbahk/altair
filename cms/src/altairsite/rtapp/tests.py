# -*- coding:utf-8 -*-

import unittest
from datetime import datetime
from altaircms.testing import DummyRequest
from .builders import (
    GenreListResponseBuilder,
    PerformanceGroupListResponseBuilder,
    EventDetailResponseBuilder
)

class RTAppGenreListResponseBuilderTest(unittest.TestCase):
    def setUp(self):
        from altaircms.models import Genre
        from altaircms.page.models import PageSet
        from altaircms.event.models import Event
        self.request = DummyRequest()
        self.genres = []
        self.genre_origin1 = Genre(
            id=1,
            name="top",
            label=u"トップ",
            origin=None,
            organization_id=8,
            is_root=True,
            display_order=1
        )
        self.genre_origin2 = Genre(
            id=2,
            name="music",
            label=u"音楽",
            origin=None,
            organization_id=8,
            is_root=False,
            display_order=1
        )
        self.genre_child1 = Genre(
            id=3,
            name="jpop",
            label=u"Jポップ",
            origin="music",
            organization_id=8,
            is_root=False,
            display_order=1,
        )
        self.genres.append(self.genre_origin1)
        self.genres.append(self.genre_origin2)
        self.genres.append(self.genre_child1)

    """TODO: Genre.ancestorsを定義する方法を調べて書き直す
    # レスポンスが正しく作成されること
    def test_it(self):
        builder = GenreListResponseBuilder()
        res = builder.build_response(self.request, self.genres)
        self.assertIsNot(res, {})

    # レスポンスに含まれるkeyが正しいこと
    def test_has_the_right_keys(self):
        builder = GenreListResponseBuilder()
        res = builder.build_response(self.request, self.genres)
        expected_keys = {"id":"testid", "label":"testlabel", "name":"testname", "hierarchy":"0", "parent_id":"1"}.keys()
        self.assertIs(0, len(set(expected_keys) ^ set(res["origin"][0].keys())), 'keys of response is wrong.')

    # レスポンスに含まれるvalueが正しいこと
    def test_has_the_right_values(self):
        builder = GenreListResponseBuilder()
        res = builder.build_response(self.request, self.genres)
        values1 = res['origin'][0].values()
        values2 = res['music'][0].values()
        self.assertTrue(None not in values1 and '' not in values1)
        self.assertTrue(None not in values2 and '' not in values2)
    """

    # inputが空でもこけないこと
    def test_input_empty(self):
        empty_g = []
        builder = GenreListResponseBuilder()
        res = builder.build_response(self.request, empty_g)
        self.assertIs(0, len(res.keys()), 'should not have keys.')


class RTAppPerformanceGroupListResponseBuilderTest(unittest.TestCase):
    def setUp(self):
        from altaircms.models import Performance, SalesSegmentGroup, SalesSegment
        from altaircms.event.models import Event
        self.request = DummyRequest(now=datetime(2015, 12, 12))
        self.performance_1 = Performance(
            id=1,
            backend_id=111,
            title="performance1",
            event_id=1,
            start_on=datetime(2015,11,11,18,0,0),
            end_on=datetime(2015,11,11,20,0,0),
            prefecture="tokyo",
            venue="Zepp Tokyo",
            event=Event(
                id=1,
                title="event1"
            )
        )
        self.performance_2 = Performance(
            id=2,
            backend_id=222,
            title="performance2",
            event_id=1,
            start_on=datetime(2015,12,12,18,0,0),
            end_on=datetime(2015,12,12,20,0,0),
            prefecture="tokyo",
            venue="Zepp Tokyo",
            event=Event(
                id=1,
                title="event1"
            )
        )
        self.performance_3 = Performance(
            id=3,
            title="performance3",
            event_id=2,
            start_on=datetime(2015,12,13,18,0,0),
            end_on=datetime(2015,12,13,20,0,0),
            prefecture="osaka",
            venue="Zepp Osaka",
            event=Event(
                id=2,
                title="event2"
            )
        )
        self.salesegment1 = SalesSegment(
            start_on=datetime(2015,10,01,0,0,0),
            end_on=datetime(2015,10,31,0,0,0),
            performance=self.performance_1,
            group=SalesSegmentGroup(name="SSG1")
        )
        self.salesegment2 = SalesSegment(
            start_on=datetime(2015,11,01,0,0,0),
            end_on=datetime(2015,11,30,0,0,0),
            performance=self.performance_2,
            group=SalesSegmentGroup(name="SSG2")
        )
        self.salesegment3 = SalesSegment(
            start_on=datetime(2015,12,01,0,0,0),
            end_on=datetime(2015,12,31,0,0,0),
            performance=self.performance_3,
            group=SalesSegmentGroup(name="SSG3")
        )
        self.events = [
            Event(
                id=1,
                backend_id=111,
                title="event1",
                performances=[self.performance_1, self.performance_2]
            ),
            Event(
                id=2,
                backend_id=222,
                title="event2",
                performances=[self.performance_3]
            )
        ]

    # 値が想定通りセットされていること（簡易確認）
    def test_it(self):
        builder = PerformanceGroupListResponseBuilder()
        res = builder.build_response(self.request, self.events, page_count=1)
        eventdict = res['events'][0]
        performdict = res['events'][0]['performances'][0]
        ssdict = res['events'][0]['performances'][0]['sales_segments'][0]
        self.assertTrue(None not in eventdict.values())
        self.assertTrue(None not in ssdict.values())


class RTAppEventDetailResponseBuilderTest(unittest.TestCase):
    def setUp(self):
        from altaircms.event.models import Event
        from altaircms.page.models import PageSet
        from altaircms.models import Performance, SalesSegment, SalesSegmentGroup
        from altaircms.plugins.widget.summary.models import SummaryWidget
        import json
        self.request = DummyRequest(now=datetime(2015, 12, 12))
        self.sales1 = SalesSegment(
            start_on=datetime(2015,10,01,0,0,0),
            end_on=datetime(2015,10,31,0,0,0),
            group=SalesSegmentGroup(name="SSG1")
        )
        self.sales2 = SalesSegment(
            start_on=datetime(2015,11,01,0,0,0),
            end_on=datetime(2015,11,30,0,0,0),
            group=SalesSegmentGroup(name="SSG2")
        )
        self.sales3 = SalesSegment(
            start_on=datetime(2015,12,01,0,0,0),
            end_on=datetime(2015,12,31,0,0,0),
            group=SalesSegmentGroup(name="SSG1")
        )
        self.performance1 = Performance(
            id=1,
            title="performance1",
            event_id=1,
            start_on=datetime(2015,11,11,18,0,0),
            end_on=datetime(2015,11,11,20,0,0),
            prefecture="tokyo",
            venue="Zepp Tokyo",
            sales=[self.sales1, self.sales2]
        )
        self.performance2 = Performance(
            id=2,
            title="performance2",
            event_id=1,
            start_on=datetime(2015,12,12,18,0,0),
            end_on=datetime(2015,12,12,20,0,0),
            prefecture="osaka",
            venue="Zepp Osaka",
            sales=[self.sales3]
        )
        self.pageset1 = PageSet(
            url="/path/to/page",
            genre_id=123
        )
        self.event1 = Event(
            id=1,
            backend_id=111,
            pagesets=[self.pageset1],
            title="sample_title",
            subtitle="sample_subtitle",
            notice=u"どこどこでイベント開催するよー",
            inquiry_for=u"問い合わせはこちら",
            performers=u'誰と誰と誰が出演予定',
            ticket_payment=u'ニコニコ払い',
            ticket_pickup=u'ニコニコ郵送',
            performances=[self.performance1, self.performance2]
        )
        self.widget1 = SummaryWidget(
            id=1,
            bound_event_id=1,
            bound_event=self.event1,
            items='''[{"label":"公演期間","content":"2014年11月15日(土) 15:00 ","notify":true},
            {"label":"販売期間: 一般発売","content":"2014年7月10日(木) 10:00 〜","notify":true},
            {"label":"説明／注意事項","content":"※未就学児のご入場はご遠慮ください。※会場内での撮影・録画・録音等は禁止されています。※ご購入されたチケットは、理由の如何を問わず、 取替・変更・キャンセルはお受けできません。※購入時、チケット代の他にシステム利用料等、各種手数料が必要となります。※中止等の場合、手数料は返金いたしませんので、予めご了承ください。","notify":true},
            {"label":"お問い合わせ先","content":"東京労音　03-xxxx-xxxx ティアラこうとう　03-xxxx-xxxx","notify":true}]'''
        )

    def test_it(self):
        from altaircms.event.event_info import EventGetEventInfoAdapter
        builder = EventDetailResponseBuilder()
        event_info = EventGetEventInfoAdapter(self.event1).get_event_info()
        res = builder.build_response(self.request, self.event1, self.event1.performances, event_info)
        for value in res.values():
            self.assertTrue(value)