# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

import mock
from altair.app.ticketing.core.models import DateCalculationBase
from altair.viewhelpers.datetime_ import DefaultDateTimeFormatter, DateTimeHelper
from markupsafe import Markup
from pyramid import testing

from .helper import SalesSearchHelper


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


class HelperTest(unittest.TestCase):
    """
    販売日程管理検索のヘルパークラスのテスト
    ----------
    """

    def setUp(self):
        self.config = testing.setUp()
        self.target = SalesSearchHelper

        self.sales_segment = DummySalesSegment(
            event=DummyEvent(
                title=u'event title1',
                setting=DummyEventSetting(
                    sales_person=u'sales person1',
                    event_operator=u'event_operator1'
                )
            ),
            performance=DummyPerformance(
                id=123,
                name=u'performance1',
                start_on=datetime(2018, 12, 20, 0, 0, 0, 0),
                venue=DummyVenue(
                    name=u'venue1'
                )
            ),
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group1'
            ),
            start_at=u'2018-12-01 00:00:00',
            end_at=u'2018-12-10 00:00:00'
        )
        self.lot_sales_segment = DummySalesSegment(
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
                    lotting_announce_datetime=datetime(2018, 12, 8, 0, 0, 0, 0)
                )
            ],
            sales_segment_group=DummySalesSegmentGroup(
                name=u'sales_segment_group3'
            ),
            start_at=u'2018-12-03 00:00:00',
            end_at=u'2018-12-07 00:00:00'
        )

    def tearDown(self):
        testing.tearDown()

    def test_disp_performance_or_lot_name(self):
        """
        disp_performance_or_lot_nameのテスト（未実施）
        ----------
        """
        # request.route_pathがモックできないため飛ばす
        pass

    def test_disp_venue_name(self):
        """
        disp_venue_nameのテスト
        一般と抽選のもの
        ----------
        """
        # パフォーマンスに紐付いている販売区分の場合
        ret = self.target.disp_venue_name(self.sales_segment)
        self.assertEqual(ret, Markup(u'<td class="span1">venue1</td>'))

        # 抽選に紐付いている販売区分の場合
        ret = self.target.disp_venue_name(self.lot_sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">-</td>"""))

    def test_disp_performance_start_or_lotting_announce_datetime(self):
        """
        disp_performance_start_or_lotting_announce_datetimeのテスト
        一般と抽選のもの
        ----------
        """
        formatter = DefaultDateTimeFormatter()
        helper = DateTimeHelper(formatter)

        # パフォーマンスに紐付いている販売区分の場合
        ret = self.target.disp_performance_start_or_lotting_announce_datetime(helper, self.sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">2018年12月20日(木) 0:00</td>"""))

        # 抽選に紐付いている販売区分の場合
        ret = self.target.disp_performance_start_or_lotting_announce_datetime(helper, self.lot_sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">2018年12月8日(土) 0:00</td>"""))

    @mock.patch('altair.app.ticketing.sales_search.util.SaleSearchUtil.get_calculated_issuing_start_at')
    @mock.patch('altair.app.ticketing.sales_search.util.SaleSearchUtil.get_issuing_start_at_dict')
    def test_disp_issuing_start_at(self, get_issuing_start_at_dict, get_calculated_issuing_start_at):
        """
        disp_issuing_start_atのテスト

        Parameters
        ----------
        get_issuing_start_at_dict: dict
            発券開始時刻のモック
        get_calculated_issuing_start_at: unicode
            計算された発券開始時刻の文字列のモック
        """
        # 決済引取方法がひとつも存在しない場合
        get_issuing_start_at_dict.return_value = {}
        get_calculated_issuing_start_at.return_value = u"2018年12月8日(土) 0:00"
        ret = self.target.disp_issuing_start_at(self.sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">-</td>"""))

        # 発券開始時刻がすべて同じ
        get_issuing_start_at_dict.return_value = {
            u'issuing_start_day_calculation_base': DateCalculationBase.Absolute.v,
            u'issuing_start_at': datetime(2018, 12, 8, 0, 0, 0, 0),
            u'issuing_interval_days': 5,
            u'issuing_interval_time': None,
            u'differented_issuing_start_at': False
        }
        ret = self.target.disp_issuing_start_at(self.sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">2018年12月8日(土) 0:00</td>"""))

        # 発券開始時刻が違う決済引取方法がある
        get_issuing_start_at_dict.return_value = {
            u'issuing_start_day_calculation_base': DateCalculationBase.Absolute.v,
            u'issuing_start_at': datetime(2018, 12, 8, 0, 0, 0, 0),
            u'issuing_interval_days': 5,
            u'issuing_interval_time': None,
            u'differented_issuing_start_at': True
        }
        ret = self.target.disp_issuing_start_at(self.sales_segment)
        self.assertEqual(ret, Markup(u"""<td class="span1">2018年12月8日(土) 0:00<br/><span style="color:red;">
            ※発券開始時刻が違う決済引取方法があります</span></td>"""))
