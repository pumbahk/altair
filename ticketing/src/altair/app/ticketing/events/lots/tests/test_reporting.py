# -*- coding:utf-8 -*-
import unittest
import mock
from testfixtures import LogCapture
from datetime import datetime
from pyramid import testing
from altair.app.ticketing.core.models import (
    ReportFrequencyEnum,
    ReportPeriodEnum,
)
from altair.app.ticketing.testing import _setup_db, _teardown_db

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
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')
        self.config.add_subscriber('altair.app.ticketing.register_globals', 'pyramid.events.BeforeRender')
        self.config.include('pyramid_mailer.testing')
        self.session = _setup_db([
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.events.lots.models",
            ])
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

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

        target = self._makeOne(sender, mailer, setting)

    def test_create_report_mail(self):
        from pyramid_mailer import get_mailer
        from datetime import datetime
        now = datetime.now()
        from altair.app.ticketing.core.models import Organization, ReportRecipient
        request = testing.DummyRequest()
        sender = u"sender@example.com"
        mailer = get_mailer(request)
        organization = Organization(id="1", short_name="testing", name="testing")
        lot = testing.DummyModel(
            id=123,
            name=u"テスト抽選",
            lotting_announce_datetime=datetime(2013, 2, 3, 12),
            organization=organization,
            event=testing.DummyModel(
                title=u"テストイベント",
            ),
            limit_wishes=5,
            sales_segment=testing.DummyModel(
                start_at=now,
                end_at=now,
                ),
            available_on=lambda now: True,
        )
        recipients=[
            ReportRecipient(
                name=u"",
                email=u"testing-recipient@example.com",
                organization_id=organization.id
            )
        ]
        setting = testing.DummyModel(
            lot_id=123,
            recipients=recipients,
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

        target = self._makeOne(sender, mailer, setting)
        target.subject_prefix = u"[testing抽選申込状況レポート]"
        result = target.create_report_mail(status)

        self.assertEqual(result.subject,
                         u"[抽選申込状況レポート|testing] テストイベント - テスト抽選")
        self.assertEqual(result.recipients,
                         [u"testing-recipient@example.com"])
        self.assertEqual(result.sender,
                         u"sender@example.com")
        self.assertIn(u"S席", result.html)


class send_lot_report_mailsTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db(modules=[
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.core.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.events.lots.models",
            ])
        self.config = testing.setUp()
        self.config.add_subscriber('altair.app.ticketing.register_globals', 'pyramid.events.BeforeRender')
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')
        self.config.add_mako_renderer('.txt')
        self.config.include('pyramid_mailer.testing')
        from altair.sqlahelper import register_sessionmaker_with_engine
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def _callFUT(self, *args, **kwargs):
        from ..reporting import send_lot_report_mails
        return send_lot_report_mails(*args, **kwargs)

    def _add_lot_entries(self):
        from altair.app.ticketing.core.models import (
            SalesSegment,
            Event,
            Performance,
            Venue,
            Site,
            Organization,
            ReportRecipient,
        )
        from altair.app.ticketing.lots.models import (
            Lot,
            LotEntry,
        )
        from altair.app.ticketing.events.lots.models import (
            LotEntryReportSetting,
        )

        organization = Organization(
            short_name="testing",
            name="testing"
        )
        self.session.add(organization)
        self.session.flush()

        lot = Lot(
            name=u"テスト抽選",
            organization=organization,
            sales_segment=SalesSegment(
                start_at=datetime(2013, 2, 1, 10, 33),
                end_at=datetime(2013, 2, 7, 10, 33),
            ),
            limit_wishes=3,
            event=Event(title=u"テストイベント"),
        )
        report_recipient = ReportRecipient(
            email=u"testing-recipient@example.com",
            organization_id=organization.id
        )
        report_setting = LotEntryReportSetting(
            lot=lot,
            frequency=ReportFrequencyEnum.Daily.v[0],
            period=ReportPeriodEnum.Normal.v[0],
            time="1030",
            recipients=[report_recipient],
        )
        self.session.add(report_recipient)
        self.session.add(report_setting)
        self.session.add(lot)
        self.session.flush()

    @mock.patch("altair.app.ticketing.events.lots.reporting.datetime")
    def test_it(self, mock_dt):
        mock_dt.now.return_value = datetime(2013, 2, 3, 10, 33)
        from pyramid_mailer import get_mailer
        self._add_lot_entries()
        request = testing.DummyRequest()
        sender = "testing@example.com"

        self._callFUT(request, sender)

        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(len(mailer.outbox[0].recipients), 1)
        self.assertEqual(mailer.outbox[0].subject, u"[抽選申込状況レポート|testing] テストイベント - テスト抽選")

    @mock.patch("altair.app.ticketing.events.lots.reporting.datetime")
    def test_it_multi(self, mock_dt):
        mock_dt.now.return_value = datetime(2013, 2, 3, 10, 33)
        from pyramid_mailer import get_mailer
        from altair.app.ticketing.core.models import Organization, ReportRecipient
        from altair.app.ticketing.events.lots.models import LotEntryReportSetting
        self._add_lot_entries()
        rs = self.session.query(LotEntryReportSetting).filter_by(time="1030").one()
        organization = self.session.query(Organization).filter_by(short_name="testing").one()
        rs.recipients.append(ReportRecipient(email=u"testing-second@example.com", organization_id=organization.id))
        self.session.flush()
        request = testing.DummyRequest()
        sender = "testing@example.com"

        self._callFUT(request, sender)

        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(len(mailer.outbox[0].recipients), 2)

    @mock.patch("altair.app.ticketing.events.lots.reporting.ReportCondition")
    @mock.patch("altair.app.ticketing.events.lots.reporting.datetime")
    def test_it_on_error(self, mock_dt, mock_cond):
        mock_dt.now.return_value = datetime(2013, 2, 3, 10, 33)
        mock_cond.side_effect = Exception()
        from pyramid_mailer import get_mailer
        self._add_lot_entries()
        request = testing.DummyRequest()
        sender = "testing@example.com"
        with LogCapture() as l:
            self._callFUT(request, sender)

        mailer = get_mailer(request)
        self.assertEqual(mailer.outbox, [])
