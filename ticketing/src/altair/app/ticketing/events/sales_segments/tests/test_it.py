# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from webob.multidict import MultiDict


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

    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('sales_segments.show', '/sales_segments/show/')
        self.config.add_route('sales_segments.edit', '/sales_segments/show/')
        self.session = _setup_db([
            "altair.app.ticketing.core.models",
        ])


    def tearDown(self):
        _teardown_db()
        testing.tearDown()

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
            Account,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            Organization,
        )
        from altair.app.ticketing.users.models import (
            User,
        )
        sales_segment = SalesSegment(
            start_at=datetime(2013, 8, 31),
            end_at=datetime(2013, 9, 30),
            sales_segment_group=SalesSegmentGroup(
                event=Event(),
                start_at=datetime(2014, 8, 31),
                end_at=datetime(2014, 9, 30),
                order_limit=1,
                upper_limit=8,
                registration_fee=100,
                printing_fee=150,
                refund_ratio=88,
                margin_ratio=99,
                account=Account(),
                payment_delivery_method_pairs=[
                    PaymentDeliveryMethodPair(
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        discount=0,
                        payment_method=PaymentMethod(name='testing-payment', fee=0),
                        delivery_method=DeliveryMethod(name='testing-delivery', fee=0)
                    ),
                    PaymentDeliveryMethodPair(
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        discount=0,
                        payment_method=PaymentMethod(name='testing-payment', fee=0),
                        delivery_method=DeliveryMethod(name='testing-delivery', fee=0)
                    ),
                ],
            ),
        )
        user = User(
            organization=Organization(
                short_name="testing",
                accounts=[
                    Account(),
                    Account(),
                    sales_segment.sales_segment_group.account,
                ],
            )
        )

        self.session.add(sales_segment)
        self.session.add(user)
        self.session.flush()
        context = testing.DummyResource(
            sales_segment=sales_segment,
            user=user,
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
                               POST=dict(
                                   end_at="",
                               ),
                               method="POST")

        target = self._makeOne(context, request)

        result = target()

        self.assertIn('form', result)
        self.assertTrue(result['form'].errors)

    def test_post_valid_form_with_using_group(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context,
                               is_xhr=False,
                               POST=MultiDict(
                                   use_default_start_at="on",
                                   end_at="",
                                   use_default_end_at="on",
                                   use_default_account_id="on",
                                   use_default_refund_ratio="on",
                                   use_default_payment_delivery_method_pairs="on",
                                   use_default_upper_limit="on",
                                   use_default_registration_fee="on",
                                   use_default_order_limit="on",
                                   use_default_printing_fee="on",
                                   use_default_margin_ratio="on",
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
            print(dict(form.data))

        self.assertFalse(isinstance(result, dict))

        sales_segment = context.sales_segment
        sales_segment_group = context.sales_segment.sales_segment_group

        self.assert_attr_equal(sales_segment, sales_segment_group, "start_at", datetime(2014, 8, 31))
        self.assert_attr_equal(sales_segment, sales_segment_group, "end_at", datetime(2014, 9, 30))
        self.assertIsNotNone(sales_segment.account_id)
        self.assert_attr_equal(sales_segment, sales_segment_group, "account_id", sales_segment_group.account_id)
        self.assert_attr_equal(sales_segment, sales_segment_group, "refund_ratio", 88)
        self.assertTrue(sales_segment.payment_delivery_method_pairs)
        self.assert_attr_equal(sales_segment, sales_segment_group, "payment_delivery_method_pairs", sales_segment_group.payment_delivery_method_pairs)
        self.assert_attr_equal(sales_segment, sales_segment_group, "upper_limit", 8)
        self.assert_attr_equal(sales_segment, sales_segment_group, "registration_fee", 100)
        self.assert_attr_equal(sales_segment, sales_segment_group, "order_limit", 1)
        self.assert_attr_equal(sales_segment, sales_segment_group, "printing_fee", 150)
        self.assert_attr_equal(sales_segment, sales_segment_group, "margin_ratio", 99)


    def test_post_valid_form_without_using_group(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context,
                               is_xhr=False,
                               POST=MultiDict({
                                   'start_at': "2013-08-31 10:10",
                                   'end_at': "2013-09-30 20:31",
                                   'account_id': context.user.organization.accounts[0].id,
                                   'refund_ratio': 10000,
                                   'payment_delivery_method_pairs[]': context.sales_segment.sales_segment_group.payment_delivery_method_pairs[0].id,
                                   'upper_limit': 4,
                                   'registration_fee': 20000,
                                   'order_limit': 10,
                                   'printing_fee': 1010,
                                   'margin_ratio': 1310,
                                   }
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
            print(dict(form.data))

        self.assertFalse(isinstance(result, dict))

        sales_segment = context.sales_segment
        sales_segment_group = context.sales_segment.sales_segment_group

        self.assertEqual(sales_segment.start_at, datetime(2013, 8, 31, 10, 10))
        self.assertEqual(sales_segment.end_at, datetime(2013, 9, 30, 20, 31))
        self.assertEqual(sales_segment.account_id, context.user.organization.accounts[0].id)
        self.assertEqual(sales_segment.refund_ratio, 10000)
        self.assertEqual(sales_segment.payment_delivery_method_pairs, [sales_segment_group.payment_delivery_method_pairs[0]])
        self.assertEqual(sales_segment.upper_limit, 4)
        self.assertEqual(sales_segment.registration_fee, 20000)
        self.assertEqual(sales_segment.order_limit, 10)
        self.assertEqual(sales_segment.printing_fee, 1010)
        self.assertEqual(sales_segment.margin_ratio, 1310)

    def assert_attr_equal(self, o1, o2, attr, actual):
        self.assertEqual(getattr(o1, attr), getattr(o2, attr), attr)
        self.assertEqual(getattr(o1, attr), actual, attr)
        self.assertEqual(getattr(o2, attr), actual, attr)
