# -*- coding:utf-8 -*-
import unittest
from datetime import datetime, time

from pyramid import testing

from .util import SaleSearchUtil


class DummySalesSegmentGroup(testing.DummyModel):
    pass


class DummySalesSegment(testing.DummyModel):
    pass


class DummyPaymentDeliveryMethodPair(testing.DummyModel):
    pass


class UtilTest(unittest.TestCase):
    """
    販売日程管理検索のユーティリティクラスのテスト
    ----------
    """

    def setUp(self):
        self.config = testing.setUp()
        self.sales_segment = DummySalesSegment(
            sales_segment_group=DummySalesSegmentGroup(
                payment_delivery_method_pairs=[
                    DummyPaymentDeliveryMethodPair(
                        issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
                        issuing_start_day_calculation_base='',
                        issuing_interval_days='',
                        issuing_interval_time=None,
                    ),
                    DummyPaymentDeliveryMethodPair(
                        issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
                        issuing_start_day_calculation_base='',
                        issuing_interval_days='',
                        issuing_interval_time=None,
                    )
                ]
            ),
            start_at=u'2018-12-01 00:00:00',
            end_at=u'2018-12-10 00:00:00'
        )
        self.sales_segment_different_pdmp = DummySalesSegment(
            sales_segment_group=DummySalesSegmentGroup(
                payment_delivery_method_pairs=[
                    DummyPaymentDeliveryMethodPair(
                        issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
                        issuing_start_day_calculation_base='',
                        issuing_interval_days='',
                        issuing_interval_time=None,
                    ),
                    DummyPaymentDeliveryMethodPair(
                        issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
                        issuing_start_day_calculation_base='1',
                        issuing_interval_days='5',
                        issuing_interval_time=time(0, 0)
                    )
                ]
            ),
            start_at=u'2018-12-01 00:00:00',
            end_at=u'2018-12-10 00:00:00'
        )

    def tearDown(self):
        testing.tearDown()

    def test_get_issuing_start_at_dict(self):
        """
        get_issuing_start_at_dictのテスト
        決済引取方法に紐付いている発券開始時刻がすべて同じ場合
        決済引取方法に紐付いている発券開始時刻が違うものが存在する場合
        ----------
        """
        # 決済引取方法に紐付いている発券開始時刻がすべて同じ場合
        issuing_start_at_dict = SaleSearchUtil.get_issuing_start_at_dict(self.sales_segment)
        self.assertEqual(issuing_start_at_dict['issuing_start_at'], datetime(2018, 12, 8, 0, 0, 0, 0))
        self.assertEqual(issuing_start_at_dict['issuing_start_day_calculation_base'], '')
        self.assertEqual(issuing_start_at_dict['issuing_interval_days'], '')
        self.assertIsNone(issuing_start_at_dict['issuing_interval_time'])
        self.assertEqual(issuing_start_at_dict['differented_issuing_start_at'], False)

        # 決済引取方法に紐付いている発券開始時刻が違うものが存在する場合
        issuing_start_at_dict = SaleSearchUtil.get_issuing_start_at_dict(self.sales_segment_different_pdmp)
        self.assertEqual(issuing_start_at_dict['issuing_start_at'], datetime(2018, 12, 8, 0, 0, 0, 0))
        self.assertEqual(issuing_start_at_dict['issuing_start_day_calculation_base'], '')
        self.assertEqual(issuing_start_at_dict['issuing_interval_days'], '')
        self.assertIsNone(issuing_start_at_dict['issuing_interval_time'])
        self.assertEqual(issuing_start_at_dict['differented_issuing_start_at'], True)

    def test_get_calculated_issuing_start_at(self):
        """
        get_issuing_start_at_dictのテスト
        決済引取方法に紐付いている発券開始時刻がすべて同じ場合
        決済引取方法に紐付いている発券開始時刻が違うものが存在する場合
        ----------
        """
        # 発券開始時刻があり（曜日表示なし）
        calculated_issuing_start_at = SaleSearchUtil.get_calculated_issuing_start_at(
            issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
            issuing_start_day_calculation_base=0,
            issuing_interval_days=None,
            issuing_interval_time=None,
            with_weekday=False
        )
        self.assertEqual(calculated_issuing_start_at, datetime(2018, 12, 8, 0, 0, 0, 0))

        # 発券開始時刻があり（曜日表示なし）
        calculated_issuing_start_at = SaleSearchUtil.get_calculated_issuing_start_at(
            issuing_start_at=datetime(2018, 12, 8, 0, 0, 0, 0),
            issuing_start_day_calculation_base=0,
            issuing_interval_days=None,
            issuing_interval_time=None,
            with_weekday=True
        )
        self.assertEqual(calculated_issuing_start_at, u"2018年12月8日(土) 0:00")
