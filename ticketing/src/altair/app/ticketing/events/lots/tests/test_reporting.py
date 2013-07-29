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

    def test_init(self):
        from datetime import datetime

        setting = testing.DummyModel(
            lot=testing.DummyModel(),
            frequency=ReportFrequencyEnum.Daily.v[0],
            period=ReportPeriodEnum.Normal.v[0],
        )
        now = datetime(2013, 1, 1, 23, 59)

        target = self._makeOne(setting, now)
        self.assertEqual(target.lot, setting.lot)

    def test_daily_normal(self):
        """ 毎日の前日分
        指定日付の前日 00:00 - 23:59 
        """

        from datetime import datetime

        setting = testing.DummyModel(
            lot=testing.DummyModel(),
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
            lot=testing.DummyModel(),
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
            lot=testing.DummyModel(),
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
            lot=testing.DummyModel(),
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Entire.v[0],
        )
        now = datetime(2013, 1, 17, 12, 34)
        
        target = self._makeOne(setting, now)

        self.assertEqual(target.from_date, datetime(2013, 1, 10, 12, 34))
        self.assertEqual(target.to_date, now)
        self.assertIsNone(target.limited_from)
        self.assertEqual(target.limited_to, '2013-01-17 12:34')

class LotEntryReporterTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_mailer.testing')
        self.config.include('altair.app.ticketing.renderers')

    def tearDown(self):
        testing.tearDown()

    def _getTarget(self):
        from ..reporting import LotEntryReporter
        return LotEntryReporter

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _add_lot_entries(self):
        pass

    def test_it(self):
        from pyramid_mailer import get_mailer
        from datetime import datetime
        sender = u"sender@example.com"
        request = testing.DummyRequest()
        mailer = get_mailer(request)
        setting = testing.DummyModel(
            lot=testing.DummyModel(),
        )
        now = datetime(2013, 2, 3)

        target = self._makeOne(sender, mailer, setting, now)

    def test_create_report_mail(self):
        from pyramid_mailer import get_mailer
        from datetime import datetime
        request = testing.DummyRequest()
        sender = u"sender@example.com"
        mailer = get_mailer(request)
        lot = testing.DummyModel(
            id=123,
            name=u"テスト抽選",
            lotting_announce_datetime=datetime(2013, 2, 3, 12),
            event=testing.DummyModel(
                title=u"テストイベント",
            ),
            limit_wishes=5,
        )
        setting = testing.DummyModel(
            lot_id=123,
            recipient=u"testing-recipient@example.com",
            lot=lot,
        )
        now = datetime(2013, 2, 3)

        status = testing.DummyModel(
            total_entries=1,
            elected_count=2,
            ordered_count=3,
            reserved_count=4,
            canceled_count=5,
            lot=lot,
            total_quantity=100,
            wish_statuses=[
                testing.DummyModel(quantity=10),
                testing.DummyModel(quantity=15),
                testing.DummyModel(quantity=20),
                testing.DummyModel(quantity=25),
                testing.DummyModel(quantity=30),
            ],
            performance_seat_type_statuses=[
                testing.DummyModel(
                    performance=testing.DummyModel(
                        start_on=datetime(2013, 1, 20),
                        venue=testing.DummyModel(
                            name=u"テスト会場",
                        ),
                    ),
                    seat_type=testing.DummyModel(
                        name=u"S席"
                    ),
                    entry_quantity=100,
                    wish_statuses=[
                        testing.DummyModel(entry_quantity=10),
                        testing.DummyModel(entry_quantity=15),
                        testing.DummyModel(entry_quantity=20),
                        testing.DummyModel(entry_quantity=25),
                        testing.DummyModel(entry_quantity=30),
                    ],
                    elected_quantity=10,
                    ordered_quantity=20,
                    reserved_quantity=30,
                    canceled_quantity=40,
                ),
            ],
        )

        target = self._makeOne(sender, mailer, setting, now)
        target.subject_prefix = u"[testing抽選申込状況レポート]"
        result = target.create_report_mail(status)

        self.assertEqual(result.subject,
                         u"[testing抽選申込状況レポート] テスト抽選")
        self.assertEqual(result.recipients,
                         [u"testing-recipient@example.com"])
        self.assertEqual(result.sender,
                         u"sender@example.com")
        print result.html
        self.assertIn(u"S席", result.html)
