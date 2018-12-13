# -*- coding:utf-8 -*-
import unittest

import mock
from pyramid import testing

from .exporter import CSVExporter


class DummyEvent(testing.DummyModel):
    pass


class DummyLot(testing.DummyModel):
    pass


class DummyEventSetting(testing.DummyModel):
    pass


class DummySalesSegmentGroup(testing.DummyModel):
    pass


class DummySalesSegment(testing.DummyModel):
    pass


class DummyPerformance(testing.DummyModel):
    pass


class DummyVenue(testing.DummyModel):
    pass


class ExporterTest(unittest.TestCase):
    """
    販売日程管理検索のダウンロード用クラスのテスト
    ----------
    """

    def setUp(self):
        self.config = testing.setUp()
        sales_segment1 = DummySalesSegment(
            event=DummyEvent(
                title=u'event title1',
                setting=DummyEventSetting(
                    sales_person=u'sales person1',
                    event_operator=u'event_operator1'
                )
            ),
            performance=DummyPerformance(
                name=u'performance1',
                start_on=u'2018-12-08 00:00:00',
                venue=DummyVenue(
                    name=u'venue1'
                )
            ),
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group1'
            ),
            start_at=u'2018-12-01 00:00:00',
            end_at=u'2018-12-05 00:00:00'
        )
        sales_segment2 = DummySalesSegment(
            event=DummyEvent(
                title=u'event title2',
                setting=DummyEventSetting(
                    sales_person=u'sales person2',
                    event_operator=u'event_operator2'
                )
            ),
            performance=DummyPerformance(
                name=u'performance2',
                start_on=u'2018-12-09 00:00:00',
                venue=DummyVenue(
                    name=u'venue2'
                )
            ),
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group2'
            ),
            start_at=u'2018-12-02 00:00:00',
            end_at=u'2018-12-06 00:00:00'
        )
        sales_segment3 = DummySalesSegment(
            event=DummyEvent(
                title=u'event title3',
                setting=DummyEventSetting(
                    sales_person=u'sales person3',
                    event_operator=u'event_operator3'
                )
            ),
            performance=None,
            lots=[
                DummyLot(
                    name=u'lots3',
                    lotting_announce_datetime=u'2018-12-08 00:00:00'
                )
            ],
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group3'
            ),
            start_at=u'2018-12-03 00:00:00',
            end_at=u'2018-12-07 00:00:00'
        )
        sales_segment4 = DummySalesSegment(
            event=DummyEvent(
                title=u'event title4',
                setting=DummyEventSetting(
                    sales_person=u'sales person4',
                    event_operator=u'event_operator4'
                )
            ),
            performance=None,
            lots=[
                DummyLot(
                    name=u'lots4',
                    lotting_announce_datetime=u'2018-12-09 00:00:00'
                )
            ],
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group4'
            ),
            start_at=u'2018-12-04 00:00:00',
            end_at=u'2018-12-08 00:00:00'
        )
        self.target_performance = CSVExporter([sales_segment1, sales_segment2])
        self.target_lots = CSVExporter([sales_segment3, sales_segment4])

    def tearDown(self):
        testing.tearDown()

    @mock.patch('altair.app.ticketing.sales_search.util.SaleSearchUtil.get_issuing_start_at_dict')
    def test_iterate(self, get_issuing_start_at_dict):
        """
        パフォーマンスの場合のテスト

        Parameters
        ----------
        get_issuing_start_at_dict: mock
            get_issuing_start_at_dictでの決済引取方法のところをモック

        """
        get_issuing_start_at_dict.return_value = {}
        for num, ordered_dict in enumerate(self.target_performance):
            if num == 0:
                self.assertEqual(ordered_dict[u"イベント名"], u'event title1')
                self.assertEqual(ordered_dict[u"公演名（抽選名）"], u'performance1')
                self.assertEqual(ordered_dict[u"販売区分名"], u'sales_segment_group1')
                self.assertEqual(ordered_dict[u"会場名"], u'venue1')
                self.assertEqual(ordered_dict[u"公演日（抽選当選日）"], u'2018-12-08 00:00:00')
                self.assertEqual(ordered_dict[u"販売開始"], u'2018-12-01 00:00:00')
                self.assertEqual(ordered_dict[u"販売終了"], u'2018-12-05 00:00:00')
                self.assertEqual(ordered_dict[u"発券開始日時"], u'')
                self.assertEqual(ordered_dict[u"営業担当"], u'sales person1')
                self.assertEqual(ordered_dict[u"登録担当"], u'event_operator1')
            elif num == 1:
                self.assertEqual(ordered_dict[u"イベント名"], u'event title2')
                self.assertEqual(ordered_dict[u"公演名（抽選名）"], u'performance2')
                self.assertEqual(ordered_dict[u"販売区分名"], u'sales_segment_group2')
                self.assertEqual(ordered_dict[u"会場名"], u'venue2')
                self.assertEqual(ordered_dict[u"公演日（抽選当選日）"], u'2018-12-09 00:00:00')
                self.assertEqual(ordered_dict[u"販売開始"], u'2018-12-02 00:00:00')
                self.assertEqual(ordered_dict[u"販売終了"], u'2018-12-06 00:00:00')
                self.assertEqual(ordered_dict[u"発券開始日時"], u'')
                self.assertEqual(ordered_dict[u"営業担当"], u'sales person2')
                self.assertEqual(ordered_dict[u"登録担当"], u'event_operator2')

    @mock.patch('altair.app.ticketing.sales_search.util.SaleSearchUtil.get_issuing_start_at_dict')
    def test_iterate2(self, get_issuing_start_at_dict):
        """
        パフォーマンスの場合のテスト

        Parameters
        ----------
        get_issuing_start_at_dict: mock
            get_issuing_start_at_dictでの決済引取方法のところをモック

        """
        get_issuing_start_at_dict.return_value = {}
        for num, ordered_dict in enumerate(self.target_lots):
            if num == 0:
                self.assertEqual(ordered_dict[u"イベント名"], u'event title3')
                self.assertEqual(ordered_dict[u"公演名（抽選名）"], u'lots3')
                self.assertEqual(ordered_dict[u"販売区分名"], u'sales_segment_group3')
                self.assertEqual(ordered_dict[u"会場名"], u'-')
                self.assertEqual(ordered_dict[u"公演日（抽選当選日）"], u'2018-12-08 00:00:00')
                self.assertEqual(ordered_dict[u"販売開始"], u'2018-12-03 00:00:00')
                self.assertEqual(ordered_dict[u"販売終了"], u'2018-12-07 00:00:00')
                self.assertEqual(ordered_dict[u"発券開始日時"], u'')
                self.assertEqual(ordered_dict[u"営業担当"], u'sales person3')
                self.assertEqual(ordered_dict[u"登録担当"], u'event_operator3')
            elif num == 1:
                self.assertEqual(ordered_dict[u"イベント名"], u'event title4')
                self.assertEqual(ordered_dict[u"公演名（抽選名）"], u'lots4')
                self.assertEqual(ordered_dict[u"販売区分名"], u'sales_segment_group4')
                self.assertEqual(ordered_dict[u"会場名"], u'-')
                self.assertEqual(ordered_dict[u"公演日（抽選当選日）"], u'2018-12-09 00:00:00')
                self.assertEqual(ordered_dict[u"販売開始"], u'2018-12-04 00:00:00')
                self.assertEqual(ordered_dict[u"販売終了"], u'2018-12-08 00:00:00')
                self.assertEqual(ordered_dict[u"発券開始日時"], u'')
                self.assertEqual(ordered_dict[u"営業担当"], u'sales person4')
                self.assertEqual(ordered_dict[u"登録担当"], u'event_operator4')
