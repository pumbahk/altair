# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest


class SalesSegmentsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.renderers')
        self.session = _setup_db([
            "altair.app.ticketing.core.models",
        ])
        import sqlalchemy
        sqlalchemy.orm.configure_mappers()

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from ..views import SalesSegments
        return SalesSegments

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_new_post(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import (
            Organization,
            Account,
            Event,
            SalesSegmentGroup,
            SalesSegment,
            Performance,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
        )
        from altair.app.ticketing.users.models import (
            MemberGroup,
        )

        self.config.add_route('sales_segments.index', 'sales_segments/index')
        organization = Organization(short_name='testing')
        account = Account(organization=organization)
        event = Event(organization=organization)
        pdmp = PaymentDeliveryMethodPair(system_fee=0,
                                         transaction_fee=0,
                                         delivery_fee=0,
                                         discount=0,
                                         payment_method=PaymentMethod(fee=0,
                                                                      name="testing-payment"),
                                         delivery_method=DeliveryMethod(fee=0,
                                                                        name="testing-delivery"))
        membergroup = MemberGroup()
        sales_segment_group=SalesSegmentGroup(event=event,
                                              organization=organization,
                                              payment_delivery_method_pairs=[pdmp],
                                              membergroups=[membergroup])
        performance = Performance(event=event,
                                  start_on=datetime(2013, 1, 1))

        self.session.add(organization)
        self.session.flush()
        context = testing.DummyResource(
            event=event,
            performance=performance,
            sales_segment_group=sales_segment_group,
            user=testing.DummyModel(organization=organization),
        )
        request = DummyRequest(context=context,
                               POST={
                                   'start_at': '2013-05-05 00:00',
                                   'end_at': '2013-12-31 23:59',
                                   'payment_delivery_method_pairs': str(pdmp.id),
                                   'account_id': str(account.id),
                               })

        target = self._makeOne(context, request)

        result = target.new_post()
        if isinstance(result, dict):
            for e, msgs in result['form'].errors.items():
                print e,
                for m in msgs:
                    print m

        self.assertEqual(result.location, '/sales_segments/index?performance_id=%d' % performance.id)
        self.assertEqual(request.session.pop_flash(), [u"販売区分を作成しました"])

        ss = self.session.query(SalesSegment).one()

        self.assertEqual(ss.sales_segment_group, sales_segment_group)
        self.assertEqual(ss.organization, organization)
        self.assertEqual(ss.event, event)
        self.assertEqual(ss.membergroups, [membergroup])

    def test_new_post_xhr(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import (
            Organization,
            Account,
            Event,
            SalesSegmentGroup,
            SalesSegment,
            Performance,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
        )
        from altair.app.ticketing.users.models import (
            MemberGroup,
        )

        self.config.add_route('sales_segments.index', 'sales_segments/index')
        organization = Organization(short_name='testing')
        account = Account(organization=organization)
        event = Event(organization=organization)
        pdmp = PaymentDeliveryMethodPair(system_fee=0,
                                         transaction_fee=0,
                                         delivery_fee=0,
                                         discount=0,
                                         payment_method=PaymentMethod(fee=0,
                                                                      name="testing-payment"),
                                         delivery_method=DeliveryMethod(fee=0,
                                                                        name="testing-delivery"))
        membergroup = MemberGroup()
        sales_segment_group=SalesSegmentGroup(event=event,
                                              organization=organization,
                                              payment_delivery_method_pairs=[pdmp],
                                              membergroups=[membergroup])
        performance = Performance(event=event,
                                  start_on=datetime(2013, 1, 1))

        self.session.add(organization)
        self.session.flush()
        context = testing.DummyResource(
            event=event,
            performance=performance,
            sales_segment_group=sales_segment_group,
            user=testing.DummyModel(organization=organization),
        )
        request = DummyRequest(context=context,
                               POST={
                                   'start_at': '2013-05-05 00:00',
                                   'end_at': '2013-12-31 23:59',
                                   'payment_delivery_method_pairs': str(pdmp.id),
                                   'account_id': str(account.id),
                               })

        target = self._makeOne(context, request)

        result = target.new_post_xhr()
        if isinstance(result, dict):
            for e, msgs in result['form'].errors.items():
                print e,
                for m in msgs:
                    print m


        self.assertEqual(request.session.pop_flash(), [u"販売区分を作成しました"])

        ss = self.session.query(SalesSegment).one()

        self.assertEqual(ss.sales_segment_group, sales_segment_group)
        self.assertEqual(ss.organization, organization)
        self.assertEqual(ss.event, event)
        self.assertEqual(ss.membergroups, [membergroup])


class EditSalesSegmentTests(unittest.TestCase):

    def _getTarget(self):
        from ..views import EditSalesSegment
        return EditSalesSegment

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def assert_data(self, form, name, actual):
        self.assertEqual(form[name].data, actual)

    def _context(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import (
            SalesSegment,
            SalesSegmentGroup,
            Event,
        )
        sales_segment = SalesSegment(
            start_at=datetime(2013, 8, 31),
            end_at=datetime(2013, 9, 30),
            sales_segment_group=SalesSegmentGroup(
                event=Event(),
            ),
        )
        context = testing.DummyResource(
            sales_segment=sales_segment,
        )
        return context

    def test_get(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context)
        target = self._makeOne(context, request)

        result = target()

        self.assertIn('form', result)
        form = result['form']


        self.assert_data(form, 'start_at', datetime(2013, 8, 31))
        self.assert_data(form, 'end_at', datetime(2013, 9, 30))

    def test_post_invalid_form(self):
        context = self._context()
        request = DummyRequest(context=context,
                               POST=dict(),
                               method="POST")

        target = self._makeOne(context, request)

        result = target()

        self.assertIn('form', result)
        self.assertTrue(result['form'].errors)

    def test_post_valid_form(self):
        context = self._context()
        request = DummyRequest(context=context,
                               POST=dict(
                               ),
                               method="POST")

        target = self._makeOne(context, request)

        result = target()
        if isinstance(result, dict):
            form = result['form']
            for name, errors in form.errors.items():
                print name,
                for e in errors:
                    print e

        #self.assertFalse(isinstance(result, dict))
