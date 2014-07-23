import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db


class LotEntryReportSettingFormTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.orders.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..forms import LotEntryReportSettingForm
        return LotEntryReportSettingForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _organization(self):
        from altair.app.ticketing.core.models import (
            Organization,
            ReportRecipient,
        )
        organization = Organization(
            short_name=u'testing',
        )
        self.session.add(organization)
        self.session.flush()

        recipient = ReportRecipient(
            name=u"testing-recipient",
            email=u"testing-recipient@example.com",
            organization_id=organization.id
        )
        self.session.add(recipient)
        self.session.flush()
        return organization

    def test_init(self):
        formdata = None
        obj = None
        organization = self._organization()
        recipient = organization.report_recipients[0]
        context = testing.DummyResource(
            organization=testing.DummyModel(id=organization.id)
            )
        target = self._makeOne(formdata, obj, context=context)

        self.assertEqual(target.recipients.choices,
                         [(recipient.id, u'{} <{}>'.format(recipient.name, recipient.email))])
        

    def test_validate_recipients_without_param(self):
        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)

        field = testing.DummyModel(data=False)
        target.validate_recipients(field)

    def test_validate_recipients_with_param_registered(self):
        from wtforms.validators import ValidationError

        from altair.app.ticketing.core.models import (
            ReportFrequencyEnum,
            ReportPeriodEnum,
            Event,
        )
        from altair.app.ticketing.lots.models import (
            Lot,
        )
        from altair.app.ticketing.events.lots.models import (
            LotEntryReportSetting,
        )
        organization = self._organization()
        recipient = organization.report_recipients[0]
        event = Event()
        lot = Lot(event=event)
        time = "1000"
        day_of_week = 1
        setting = LotEntryReportSetting(
            event=event,
            lot=lot,
            time=time,
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Normal.v[0],
            day_of_week=day_of_week,
            recipients=[recipient],
        )
        self.session.add(setting)
        self.session.flush()

        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)
        target.event_id.data = event.id
        target.lot_id.data = lot.id
        target.report_hour.data = time[0:2]
        target.report_minute.data = time[2:]
        target.frequency.data = ReportFrequencyEnum.Weekly.v[0]
        target.day_of_week.data = day_of_week
        target.recipients.data = [recipient.id]

        field = testing.DummyModel(data=[recipient.id])
        assert self.session.query(LotEntryReportSetting).count() == 1

        try:
            target.validate_recipients(field)
            self.fail()
        except ValidationError:
            pass

    def test_validate_email_without_param(self):
        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)

        field = testing.DummyModel(data=False)
        target.validate_email(field)

    def test_validate_email_with_param_registered(self):
        from wtforms.validators import ValidationError

        from altair.app.ticketing.core.models import (
            ReportFrequencyEnum,
            ReportPeriodEnum,
            Event,
        )
        from altair.app.ticketing.lots.models import (
            Lot,
        )
        from altair.app.ticketing.events.lots.models import (
            LotEntryReportSetting,
        )
        organization = self._organization()
        recipient = organization.report_recipients[0]
        event = Event()
        lot = Lot(event=event)
        time = "1000"
        day_of_week = 1
        email = "testing-recipient@example.com"

        setting = LotEntryReportSetting(
            event=event,
            lot=lot,
            time=time,
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Normal.v[0],
            day_of_week=day_of_week,
            recipients=[recipient],
        )
        self.session.add(setting)
        self.session.flush()

        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)
        target.event_id.data = event.id
        target.lot_id.data = lot.id
        target.report_hour.data = time[0:2]
        target.report_minute.data = time[2:]
        target.frequency.data = ReportFrequencyEnum.Weekly.v[0]
        target.day_of_week.data = day_of_week
        target.email.data = email

        field = testing.DummyModel(data=email)
        assert self.session.query(LotEntryReportSetting).count() == 1

        try:
            target.validate_email(field)
            self.fail()
        except ValidationError:
            pass
