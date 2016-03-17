# -*- coding: utf-8 -*-
import unittest
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db


class LotFormTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.orders.models',
        ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from ..forms import LotForm
        return LotForm

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

    @mock.patch('altair.app.ticketing.events.lots.forms.get_plugin_names')
    def test_create_lot_10993(self, get_plugin_names):
        from datetime import datetime
        from altair.app.ticketing.core.models import Organization, Event, SalesSegmentGroup, SalesSegmentGroupSetting
        from altair.app.ticketing.users.models import Membership, MemberGroup, MemberGroup_SalesSegment, MemberGroup_SalesSegmentGroup

        get_plugin_names.return_value = [
            ('a', 'a'),
            ('b', 'b'),
            ]

        organization = self._organization()
        event = Event(organization=organization)
        membership = Membership(organization=organization, name='membership')
        membergroup = MemberGroup(membership=membership, name='membergroup')
        sales_segment_group = SalesSegmentGroup(
            organization=organization,
            event=event,
            name='sales_segment_group',
            membergroups=[membergroup],
            start_at=datetime(2015, 1, 1, 0, 0, 0),
            end_at=datetime(2015,1, 2, 0, 0, 0),
            public=True,
            setting=SalesSegmentGroupSetting()
            )
        self.session.add(sales_segment_group)
        self.session.flush()

        request = testing.DummyRequest()
        context = testing.DummyResource(request=request)
        target = self._makeOne(context=context)
        target.name.data = 'test'
        target.limit_wishes.data = 1
        target.entry_limit.data = 1
        target.description.data = 'test'
        target.lotting_announce_datetime.data = datetime(2015, 1, 1, 0, 0, 0)
        target.lotting_announce_timezone.data = datetime(2015, 1, 1, 0, 0, 0)
        target.custom_timezone_label.data = ''
        target.auth_type.data = ''
        target.sales_segment_group_id.data = sales_segment_group.id
        target.start_at.data = None
        target.use_default_start_at.data = True
        target.end_at.data = None
        target.use_default_end_at.data = True
        target.max_quantity.data = 1
        target.auth3d_notice.data = ''

        lot = target.create_lot(event)
        sales_segment = lot.sales_segment
        self.assertEqual(sales_segment.sales_segment_group_id, sales_segment_group.id)
        self.assertEqual(sales_segment.start_at, sales_segment_group.start_at)
        self.assertEqual(sales_segment.end_at, sales_segment_group.end_at)
        self.assertTrue(self.session.query(MemberGroup_SalesSegmentGroup).count() > 0)
        self.assertEqual(sales_segment.membergroups, sales_segment_group.membergroups)

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
        from altair.app.ticketing.core.models import Organization, ReportRecipient
        organization = Organization(short_name=u'testing')
        self.session.add(organization)
        self.session.flush()

        recipient = ReportRecipient(
            name=u"名前1",
            email=u"testing-recipient@example.com",
            organization_id=organization.id
        )
        recipient2 = ReportRecipient(
            name=u"名前2",
            email=u"testing-recipient2@example.com",
            organization_id=organization.id
        )
        self.session.add(recipient)
        self.session.add(recipient2)
        self.session.flush()
        return organization

    def test_init(self):
        formdata = None
        obj = None
        organization = self._organization()
        context = testing.DummyResource(
            organization=testing.DummyModel(id=organization.id)
            )
        target = self._makeOne(formdata, obj, context=context)
        self.assertEqual(target is not None, True)

    def test_validate_recipients_without_param(self):
        formdata = None
        obj = None
        target = self._makeOne(formdata, obj)

        field = testing.DummyModel(data="")
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
        recipient = [organization.report_recipients[0], organization.report_recipients[1]]
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
            recipients=recipient,
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
        target.recipients.data = u"名前1,testing-recipient@example.com\n名前2,testing-recipient2@example.com"

        field = testing.DummyModel(data=target.recipients.data)
        assert self.session.query(LotEntryReportSetting).count() == 1

        try:
            target.validate_recipients(field)
        except ValidationError:
            self.fail()
