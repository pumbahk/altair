import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db


class LotEntryReportMailFormTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..forms import LotEntryReportMailForm
        return LotEntryReportMailForm

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _organization(self):
        from altair.app.ticketing.core.models import (
            Organization,
            Operator,
        )
        organization = Organization(
            short_name='testing',
            operators=[
                Operator(name="testing-operator"),
            ]
        )
        self.session.add(organization)
        self.session.flush()
        return organization

    def test_init(self):
        formdata = None
        obj = None
        organization = self._organization()
        operator = organization.operators[0]
        target = self._makeOne(formdata, obj, organization_id=organization.id)

        self.assertEqual(target.operator_id.choices,
                         [('', ''), (operator.id, operator.name)])
        

    def test_validate_operator_id_without_param(self):
        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)

        field = testing.DummyModel(data=False)
        target.validate_operator_id(field)

    def test_validate_operator_id_with_param_registered(self):
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
        operator = organization.operators[0]
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
            operator=operator,
        )
        self.session.add(setting)
        self.session.flush()

        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)
        target.event_id.data = event.id
        target.lot_id.data = lot.id
        target.time.data = time
        target.frequency.data = ReportFrequencyEnum.Weekly.v[0]
        target.day_of_week.data = day_of_week
        target.operator_id.data = operator.id

        field = testing.DummyModel(data=True)
        assert self.session.query(LotEntryReportSetting).count() == 1

        try:
            target.validate_operator_id(field)
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

        event = Event()
        lot = Lot(event=event)
        time = "1000"
        day_of_week = 1
        email = 'testing@example.com'

        setting = LotEntryReportSetting(
            event=event,
            lot=lot,
            time=time,
            frequency=ReportFrequencyEnum.Weekly.v[0],
            period=ReportPeriodEnum.Normal.v[0],
            day_of_week=day_of_week,
            email=email,
        )
        self.session.add(setting)
        self.session.flush()

        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)
        target.event_id.data = event.id
        target.lot_id.data = lot.id
        target.time.data = time
        target.frequency.data = ReportFrequencyEnum.Weekly.v[0]
        target.day_of_week.data = day_of_week
        target.email.data = email

        field = testing.DummyModel(data=True)
        assert self.session.query(LotEntryReportSetting).count() == 1

        try:
            target.validate_email(field)
            self.fail()
        except ValidationError:
            pass
