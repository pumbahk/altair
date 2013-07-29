# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from altair.app.ticketing.core.models import (
    ReportFrequencyEnum,
    ReportPeriodEnum,
)

class ReportConditionTests(unittest.TestCase):
    """ 
    毎日、毎週
    指定期間（前日分・前週分）
    全期間（販売開始～送信日時まで）
    """

    def _getTarget(self):
        from ..reporting import ReportCondition
        return ReportCondition

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


    def test_daily_normal(self):
        """ 毎日の前日分
        指定日付の前日 00:00 - 23:59 
        """

        from datetime import datetime

        setting = testing.DummyModel(
            frequency=ReportFrequencyEnum.Daily.v[0],
            period=ReportPeriodEnum.Normal.v[0],
        )
        now = datetime(2013, 1, 1, 23, 59)
        
        target = self._makeOne(setting, now)

        self.assertEqual(target.from_date, datetime(2012, 12, 31, 23, 59))
        self.assertEqual(target.to_date, datetime(2012, 12, 31, 23, 59))
        self.assertEqual(target.limited_from, '2012-12-31 00:00')
        self.assertEqual(target.limited_to, '2012-12-31 23:59')

    def test_daily_entire(self):
        """ 毎日の全期間
        開始指定なし
        指定日付まで
        """

        from datetime import datetime

        setting = testing.DummyModel(
            frequency=ReportFrequencyEnum.Daily.v[0],
            period=ReportPeriodEnum.Entire.v[0],
        )
        now = datetime(2013, 1, 1, 12, 59)
        
        target = self._makeOne(setting, now)

        self.assertEqual(target.from_date, now)
        self.assertEqual(target.to_date, now)
        self.assertIsNone(target.limited_from)
        self.assertEqual(target.limited_to, '2013-01-01 12:59')

    def test_weekly_normal(self):
        """ 毎週の前週分
        指定日付の7日前 00:00 - 前日23:59 

        """
        from datetime import datetime

        setting = testing.DummyModel(
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Normal.v[0],
        )
        now = datetime(2013, 1, 17, 23, 59)
        
        target = self._makeOne(setting, now)

        self.assertEqual(target.from_date, datetime(2013, 1, 10, 23, 59))
        self.assertEqual(target.to_date, datetime(2013, 1, 16, 23, 59))
        self.assertEqual(target.limited_from, '2013-01-10 00:00')
        self.assertEqual(target.limited_to, '2013-01-16 23:59')

    def test_weekly_entire(self):
        """ 毎日の全期間
        開始指定なし
        指定日付まで
        """
        from datetime import datetime

        setting = testing.DummyModel(
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Entire.v[0],
        )
        now = datetime(2013, 1, 17, 12, 34)
        
        target = self._makeOne(setting, now)

        self.assertEqual(target.from_date, datetime(2013, 1, 10, 12, 34))
        self.assertEqual(target.to_date, now)
        self.assertIsNone(target.limited_from)
        self.assertEqual(target.limited_to, '2013-01-17 12:34')

