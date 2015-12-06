# -*- coding:utf-8 -*-

import unittest
from pyramid import testing
from zope.interface import directlyProvides
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from webob.multidict import MultiDict


class SalesSegmentsTests(unittest.TestCase):

    def setUp(self):
        self.session = _setup_db([
            "altair.app.ticketing.orders.models",
            "altair.app.ticketing.cart.models",
            "altair.app.ticketing.lots.models",
            "altair.app.ticketing.core.models",
        ])
        self.config = testing.setUp()
        self.config.include('pyramid_mako')
        self.config.add_mako_renderer('.html')
        self.config.add_route('sales_segments.show', '/sales_segments/show/')
        self.config.add_route('sales_segments.edit', '/sales_segments/edit/')

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from ..views import SalesSegments
        return SalesSegments

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _makeRequest(self, *args, **kwargs):
        from pyramid.interfaces import IRoutesMapper
        request = DummyRequest(*args, **kwargs)
        mapper = request.registry.queryUtility(IRoutesMapper)
        request.environ['PATH_INFO'] = request.path_info
        info = mapper(request)
        request.matched_route = info['route']
        return request

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
            DateCalculationBase,
        )
        from altair.app.ticketing.users.models import (
            MemberGroup,
        )
        from ..resources import ISalesSegmentAdminResource

        self.config.add_route('sales_segments.new', 'sales_segments/new')
        self.config.add_route('sales_segments.index', 'sales_segments/index')
        organization = Organization(short_name='testing')
        account = Account(organization=organization)
        event = Event(organization=organization)
        pdmp = PaymentDeliveryMethodPair(
            system_fee=0,
            transaction_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            discount=0,
            payment_method=PaymentMethod(fee=0, name="testing-payment"),
            delivery_method=DeliveryMethod(fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0, name="testing-delivery"),
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
            )
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
            organization=organization
        )
        directlyProvides(context, ISalesSegmentAdminResource)
        request = self._makeRequest(context=context,
                               path='/sales_segments/new',
                               POST={
                                   'performance_id': context.performance.id,
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
                    print m.encode('utf-8')

        self.assertEqual(result.location, '/sales_segments/index?performance_id=%d' % performance.id)
        self.assertEqual(request.session.pop_flash(), [u"販売区分を作成しました"])

        ss = self.session.query(SalesSegment).one()

        self.assertEqual(ss.sales_segment_group, sales_segment_group)
        self.assertEqual(ss.organization, organization)
        self.assertEqual(ss.event, event)
        self.assertEqual(ss.membergroups, [membergroup])

    def test_new_post(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import (
            Organization,
            Account,
            Event,
            SalesSegmentGroup,
            SalesSegmentGroupSetting,
            SalesSegment,
            Performance,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            DateCalculationBase,
        )
        from altair.app.ticketing.users.models import (
            MemberGroup,
        )
        from ..resources import ISalesSegmentAdminResource

        self.config.add_route('sales_segments.new', 'sales_segments/new')
        self.config.add_route('sales_segments.index', 'sales_segments/index')
        organization = Organization(short_name='testing')
        account = Account(organization=organization)
        event = Event(organization=organization)
        pdmp = PaymentDeliveryMethodPair(
            system_fee=0,
            transaction_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            discount=0,
            payment_method=PaymentMethod(fee=0, name="testing-payment"),
            delivery_method=DeliveryMethod(fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0, name="testing-delivery"),
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
            )
        membergroup = MemberGroup()
        sales_segment_group=SalesSegmentGroup(
            event=event,
            organization=organization,
            payment_delivery_method_pairs=[pdmp],
            membergroups=[membergroup],
            setting=SalesSegmentGroupSetting()
            )
        performance = Performance(event=event,
                                  start_on=datetime(2013, 1, 1))

        self.session.add(organization)
        self.session.flush()
        context = testing.DummyResource(
            event=event,
            performance=performance,
            sales_segment_group=sales_segment_group,
            organization=organization
        )
        directlyProvides(context, ISalesSegmentAdminResource)
        request = self._makeRequest(context=context,
                               path='/sales_segments/new',
                               POST={
                                   'performance_id': context.performance.id,
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
                    print m.encode('utf-8')


        self.assertEqual(request.session.pop_flash(), [u"販売区分を作成しました"])

        ss = self.session.query(SalesSegment).one()

        self.assertEqual(ss.sales_segment_group, sales_segment_group)
        self.assertEqual(ss.organization, organization)
        self.assertEqual(ss.event, event)
        self.assertEqual(ss.membergroups, [membergroup])

    def assert_data(self, form, name, actual):
        self.assertEqual(form[name].data, actual)

    def _context(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import (
            SalesSegment,
            SalesSegmentSetting,
            SalesSegmentGroup,
            SalesSegmentGroupSetting,
            Event,
            Performance,
            Account,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            Organization,
            DateCalculationBase,
        )
        from altair.app.ticketing.users.models import (
            User,
        )
        from ..resources import ISalesSegmentAdminResource

        account = Account()
        organization = Organization(
            short_name="testing",
            accounts=[
                Account(),
                Account(),
                account,
                ]
            )
        event=Event(organization=organization)
        performance = Performance(
            event=event,
            start_on=datetime(2014, 10, 10),
            end_on=datetime(2014, 10, 10)
            )
        sales_segment_group=SalesSegmentGroup(
            event=event,
            start_at=datetime(2014, 8, 31),
            end_at=datetime(2014, 9, 30),
            max_quantity=8,
            registration_fee=100,
            printing_fee=150,
            refund_ratio=88,
            margin_ratio=99,
            account=account,
            setting=SalesSegmentGroupSetting(
                order_limit=1,
                max_quantity_per_user=5
                ),
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(
                    system_fee=0,
                    transaction_fee=0,
                    delivery_fee_per_order=0,
                    delivery_fee_per_principal_ticket=0,
                    delivery_fee_per_subticket=0,
                    discount=0,
                    payment_method=PaymentMethod(name='testing-payment', fee=0),
                    delivery_method=DeliveryMethod(name='testing-delivery', fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                    payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                    payment_start_in_days=0,
                    payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                    payment_period_days=3,
                    issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                    issuing_interval_days=5,
                    issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
                    issuing_end_in_days=364,
                ),
                PaymentDeliveryMethodPair(
                    system_fee=0,
                    transaction_fee=0,
                    delivery_fee_per_order=0,
                    delivery_fee_per_principal_ticket=0,
                    delivery_fee_per_subticket=0,
                    discount=0,
                    payment_method=PaymentMethod(name='testing-payment', fee=0),
                    delivery_method=DeliveryMethod(name='testing-delivery', fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                    payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                    payment_start_in_days=0,
                    payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
                    payment_period_days=3,
                    issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
                    issuing_interval_days=5,
                    issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
                    issuing_end_in_days=364,

                    ),
                ]
            )

        sales_segment = SalesSegment(
            performance=performance,
            start_at=datetime(2013, 8, 31),
            end_at=datetime(2013, 9, 30),
            sales_segment_group=sales_segment_group,
            setting=SalesSegmentSetting()
            )
        user = User(
            organization=organization
        )

        self.session.add(sales_segment)
        self.session.add(user)
        self.session.flush()
        context = testing.DummyResource(
            sales_segment=sales_segment,
            sales_segment_group=sales_segment_group,
            event=event,
            performance=performance,
            organization=organization,
            user=user,
        )
        directlyProvides(context, ISalesSegmentAdminResource)
        return context

    def test_edit_get(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context, matched_route=testing.DummyResource(name='sales_segments.edit'))
        target = self._makeOne(context, request)

        result = target.edit_get()

        self.assertIn('form', result)
        form = result['form']


        self.assert_data(form, 'start_at', datetime(2013, 8, 31))
        self.assert_data(form, 'end_at', datetime(2013, 9, 30))

    def test_edit_post_invalid_form(self):
        context = self._context()
        request = DummyRequest(context=context,
                               matched_route=testing.DummyResource(name='sales_segments.edit'),
                               POST=dict(
                                   end_at="",
                               ),
                               method="POST")

        target = self._makeOne(context, request)

        result = target.edit_post()

        self.assertIn('form', result)
        self.assertTrue(result['form'].errors)

    def test_edit_post_valid_form_with_using_group(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context,
                               matched_route=testing.DummyResource(name='sales_segments.edit'),
                               is_xhr=False,
                               POST=MultiDict(
                                   use_default_start_at="on",
                                   end_at="",
                                   use_default_end_at="on",
                                   use_default_account_id="on",
                                   use_default_refund_ratio="on",
                                   use_default_payment_delivery_method_pairs="on",
                                   use_default_max_quantity="on",
                                   use_default_registration_fee="on",
                                   use_default_order_limit="on",
                                   use_default_printing_fee="on",
                                   use_default_margin_ratio="on",
                               ),
                               method="POST")

        target = self._makeOne(context, request)

        result = target.edit_post()
        if isinstance(result, dict):
            form = result['form']
            for name, errors in form.errors.items():
                print name,
                for e in errors:
                    print e.encode('utf-8')
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
        self.assert_attr_equal(sales_segment, sales_segment_group, "max_quantity", 8)
        self.assert_attr_equal(sales_segment, sales_segment_group, "registration_fee", 100)
        self.assert_attr_equal(sales_segment, sales_segment_group, "order_limit", 1)
        self.assert_attr_equal(sales_segment, sales_segment_group, "printing_fee", 150)
        self.assert_attr_equal(sales_segment, sales_segment_group, "margin_ratio", 99)


    def test_edit_post_valid_form_without_using_group(self):
        from datetime import datetime
        context = self._context()
        request = DummyRequest(context=context,
                               matched_route=testing.DummyResource(name='sales_segments.edit'),
                               is_xhr=False,
                               POST=MultiDict({
                                   'start_at': "2013-08-31 10:10",
                                   'end_at': "2013-09-30 20:31",
                                   'account_id': context.user.organization.accounts[0].id,
                                   'refund_ratio': 10000,
                                   'payment_delivery_method_pairs[]': context.sales_segment.sales_segment_group.payment_delivery_method_pairs[0].id,
                                   'max_quantity': 4,
                                   'registration_fee': 20000,
                                   'order_limit': 10,
                                   'printing_fee': 1010,
                                   'margin_ratio': 1310,
                                   }
                               ),
                               method="POST")

        target = self._makeOne(context, request)

        result = target.edit_post()
        if isinstance(result, dict):
            form = result['form']
            for name, errors in form.errors.items():
                print name,
                for e in errors:
                    print e.encode('utf-8')
            print(dict(form.data))

        self.assertFalse(isinstance(result, dict))

        sales_segment = context.sales_segment
        sales_segment_group = context.sales_segment.sales_segment_group

        self.assertEqual(sales_segment.start_at, datetime(2013, 8, 31, 10, 10))
        self.assertEqual(sales_segment.end_at, datetime(2013, 9, 30, 20, 31))
        self.assertEqual(sales_segment.account_id, context.user.organization.accounts[0].id)
        self.assertEqual(sales_segment.refund_ratio, 10000)
        self.assertEqual(sales_segment.payment_delivery_method_pairs, [sales_segment_group.payment_delivery_method_pairs[0]])
        self.assertEqual(sales_segment.max_quantity, 4)
        self.assertEqual(sales_segment.registration_fee, 20000)
        self.assertEqual(sales_segment.setting.order_limit, 10)
        self.assertEqual(sales_segment.printing_fee, 1010)
        self.assertEqual(sales_segment.margin_ratio, 1310)

    def assert_attr_equal(self, o1, o2, attr, actual):
        self.assertEqual(getattr(o1, attr), getattr(o2, attr), attr)
        self.assertEqual(getattr(o1, attr), actual, attr)
        self.assertEqual(getattr(o2, attr), actual, attr)
