# -*- coding:utf-8 -*-
import unittest
import mock
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing
from .testing import CoreTestMixin


class SalesSegmentIsDeletableTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.lots.models",
                "altair.app.ticketing.cart.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _make_one(self, exists_lots=False, exists_products=False):
        """販売区分グループを取得

        exists_lots: 紐づく抽選の有無
        exists_products: 紐づく商品の有無
        """
        from altair.app.ticketing.core.models import (
            SalesSegment,
            Product,
            )
        from altair.app.ticketing.lots.models import Lot

        ss = SalesSegment()
        if exists_lots:
            ss.lots.append(Lot())

        if exists_products:
            ss.products.append(Product())

        return ss

    def test_deletable(self):
        ss = self._make_one()
        self.assertTrue(ss.is_deletable(), '削除可能な時はTrueが返る')

    def test_undeletable_exist_lots(self):
        ss = self._make_one(exists_lots=True)
        self.assertFalse(ss.is_deletable(), '抽選がある場合は販売区分は削除できてはいけない: {}'.format(ss.lots))

    def test_undeletable_exist_products(self):
        ss = self._make_one(exists_products=True)
        self.assertFalse(ss.is_deletable(), '商品がある場合は販売区分は削除できてはいけない: {}'.format(ss.products))


class SalesSegmentTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.cart.models",
            ])
        from altair.app.ticketing.cart.models import CartSetting
        self.cart_setting = CartSetting()
        self.session.add(self.cart_setting)

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .models import SalesSegment
        return SalesSegment

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.users.models import User
        from datetime import datetime

        pdmp = PaymentDeliveryMethodPair(
            system_fee=0,
            transaction_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            discount=0,
            special_fee=0
            )
        target = self._makeOne(
            payment_delivery_method_pairs=[pdmp]
            )

        user = User()
        other = User()
        orders = []
        for i in range(2):
            cart = Cart(
                sales_segment=target,
                payment_delivery_pair=pdmp,
                cart_setting=self.cart_setting
                )
            order = Order(
                user=user, cart=cart,
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                sales_segment=target,
                payment_delivery_pair=pdmp,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            orders.append(order)

        others = []
        for i in range(2):
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                user=other, cart=cart,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            others.append(order)

        cancels = []
        for i in range(2):
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                user=user, cart=cart, canceled_at=datetime.now(),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_start_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            cancels.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_user(user).all()
        self.assertEqual(result, orders + cancels)

        result = target.query_orders_by_user(user, filter_canceled=True).all()
        self.assertEqual(result, orders)

    def test_query_orders_by_mailaddresses(self):
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from datetime import datetime

        target = self._makeOne()

        mail_addr  = 'testing@example.com'
        mail_addr_other = 'other@example.com'

        orders = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            orders.append(order)

        for i in range(2):
            shipping_address = ShippingAddress(email_2=mail_addr)
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            self.session.add(shipping_address)
            orders.append(order)

        cancels = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                cart=cart, canceled_at=datetime.now(),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            cancels.append(order)

        others = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr_other)
            cart = Cart(sales_segment=target, cart_setting=self.cart_setting)
            order = Order(
                cart=cart,
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0,
                sales_segment=target,
                issuing_start_at=datetime(1970, 1, 1),
                issuing_end_at=datetime(1970, 1, 1),
                payment_due_at=datetime(1970, 1, 1)
                )
            self.session.add(order)
            others.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_mailaddresses([mail_addr]).all()
        self.assertEqual(result, orders + cancels)

        result = target.query_orders_by_mailaddresses([mail_addr_other]).all()
        self.assertEqual(result, others)

        result = target.query_orders_by_mailaddresses([mail_addr], filter_canceled=True).all()
        self.assertEqual(result, orders)

        result = target.query_orders_by_mailaddresses([mail_addr_other], filter_canceled=True).all()
        self.assertEqual(result, others)


class PerformanceTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.cart.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .models import Performance
        return Performance

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import SalesSegment
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.users.models import User
        from datetime import datetime

        target = self._makeOne()

        user = User()
        other = User()
        orders = []
        for i in range(2):
            order = Order(
                user=user,
                sales_segment=SalesSegment(performance=target),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)

        others = []
        for i in range(2):
            order = Order(
                user=other,
                sales_segment=SalesSegment(performance=target),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            others.append(order)

        cancels = []
        for i in range(2):
            order = Order(
                user=user,
                sales_segment=SalesSegment(performance=target),
                canceled_at=datetime.now(),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            cancels.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_user(user).all()
        self.assertEqual(result, orders + cancels)

        result = target.query_orders_by_user(user, filter_canceled=True).all()
        self.assertEqual(result, orders)

    def test_query_orders_by_mailaddresses(self):
        from altair.app.ticketing.core.models import ShippingAddress, SalesSegment
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from datetime import datetime

        target = self._makeOne()

        mail_addr  = 'testing@example.com'
        mail_addr_other = 'other@example.com'

        orders = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=SalesSegment(performance=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)

        for i in range(2):
            shipping_address = ShippingAddress(email_2=mail_addr)
            order = Order(
                sales_segment=SalesSegment(performance=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)

        cancels = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=SalesSegment(performance=target),
                canceled_at=datetime.now(),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            cancels.append(order)

        others = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr_other)
            order = Order(
                sales_segment=SalesSegment(performance=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            others.append(order)


        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_mailaddresses([mail_addr]).all()
        self.assertEqual(result, orders+cancels)

        result = target.query_orders_by_mailaddresses([mail_addr_other]).all()
        self.assertEqual(result, others)

        result = target.query_orders_by_mailaddresses([mail_addr], filter_canceled=True).all()
        self.assertEqual(result, orders)

        result = target.query_orders_by_mailaddresses([mail_addr_other], filter_canceled=True).all()
        self.assertEqual(result, others)


class EventTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.cart.models",
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .models import Event
        return Event

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_sorted_performances(self):
        import random
        from altair.app.ticketing.core.models import Performance
        display_orders = range(-5, 5)

        performances = [Performance(name=str(ii), display_order=ii) for ii in display_orders]
        random.shuffle(performances)

        event = self._makeOne()
        event.performances = performances
        display_orders_result = [performance.display_order for performance in event.sorted_performances()]
        self.assertEqual(display_orders, display_orders_result)


    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import SalesSegment
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.users.models import User
        from datetime import datetime

        target = self._makeOne()

        user = User()
        other = User()
        orders = []
        for i in range(2):
            order = Order(
                user=user,
                sales_segment=SalesSegment(event=target),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)

        others = []
        for i in range(2):
            order = Order(
                user=other,
                sales_segment=SalesSegment(event=target),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            others.append(order)

        cancels = []
        for i in range(2):
            order = Order(
                user=user,
                sales_segment=SalesSegment(event=target),
                canceled_at=datetime.now(),
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            cancels.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_user(user).all()
        self.assertEqual(result, orders + cancels)

        result = target.query_orders_by_user(user, filter_canceled=True).all()
        self.assertEqual(result, orders)

    def test_query_orders_by_mailaddresses(self):
        from altair.app.ticketing.core.models import ShippingAddress, SalesSegment
        from altair.app.ticketing.orders.models import Order
        from altair.app.ticketing.cart.models import Cart
        from datetime import datetime

        target = self._makeOne()

        mail_addr  = 'testing@example.com'
        mail_addr_other = 'other@example.com'

        orders = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=SalesSegment(event=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)

        for i in range(2):
            shipping_address = ShippingAddress(email_2=mail_addr)
            order = Order(
                sales_segment=SalesSegment(event=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)

        cancels = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=SalesSegment(event=target),
                canceled_at=datetime.now(),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            cancels.append(order)

        others = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr_other)
            order = Order(
                sales_segment=SalesSegment(event=target),
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            others.append(order)


        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_mailaddresses([mail_addr]).all()
        self.assertEqual(result, orders+cancels)

        result = target.query_orders_by_mailaddresses([mail_addr_other]).all()
        self.assertEqual(result, others)

        result = target.query_orders_by_mailaddresses([mail_addr], filter_canceled=True).all()
        self.assertEqual(result, orders)

        result = target.query_orders_by_mailaddresses([mail_addr_other], filter_canceled=True).all()
        self.assertEqual(result, others)


class SalesSegmentGroupTests(unittest.TestCase):
    def _getTarget(self):
        from .models import SalesSegmentGroup
        return SalesSegmentGroup

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_sync_member_group_to_children(self):
        from .models import SalesSegment, Event, Organization
        from altair.app.ticketing.users.models import MemberGroup
        target = self._makeOne(
            organization=Organization(),
            event=Event(),
            membergroups=[
                MemberGroup(),
                MemberGroup(),
                ],
            sales_segments=[
                SalesSegment(membergroups=[MemberGroup()]),
                SalesSegment(),
                ],
        )

        target.sync_member_group_to_children()

        self.assertEqual(target.membergroups,
                         target.sales_segments[0].membergroups)
        self.assertEqual(target.membergroups,
                         target.sales_segments[1].membergroups)

        self.assertEqual(target.event,
                         target.sales_segments[0].event)
        self.assertEqual(target.event,
                         target.sales_segments[1].event)

        self.assertEqual(target.organization,
                         target.sales_segments[0].organization)
        self.assertEqual(target.organization,
                         target.sales_segments[1].organization)

    def test_new_sales_segment(self):
        from .models import Event, Organization
        from altair.app.ticketing.users.models import MemberGroup

        organization = Organization()
        event = Event()
        membergroups = [
            MemberGroup(),
            MemberGroup(),
        ]

        target = self._makeOne(
            organization=organization,
            event=event,
            membergroups=membergroups,
        )

        result = target.new_sales_segment()

        self.assertEqual(result.membergroups,
                         membergroups)
        self.assertEqual(result.event,
                         event)
        self.assertEqual(target.organization,
                         organization)

    def test_start_for_performance(self):
        from altair.app.ticketing.core.models import Performance
        from datetime import datetime, time
        performance = Performance(
            start_on=datetime(2013, 8, 31, 10, 10)
        )

        target = self._makeOne(
            start_day_prior_to_performance=10,
            start_time=time(11, 00)
        )


        result = target.start_for_performance(performance)

        self.assertEqual(result, datetime(2013, 8, 21, 11, 0))

    def test_end_for_performance(self):
        from altair.app.ticketing.core.models import Performance
        from datetime import datetime, time
        performance = Performance(
            start_on=datetime(2013, 8, 31, 10, 10)
        )

        target = self._makeOne(
            end_day_prior_to_performance=10,
            end_time=time(11, 00)
        )


        result = target.end_for_performance(performance)

        self.assertEqual(result, datetime(2013, 8, 21, 11, 0))


class DateCalculationTests(unittest.TestCase):
    def _getTarget(self):
        from .models import calculate_date_from_order_like
        return calculate_date_from_order_like

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_absolute(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        order = testing.DummyModel(
            sales_segment=testing.DummyModel(
                performance=testing.DummyModel()
                ),
            created_at=datetime(1970, 1, 1, 0, 0, 0)
            )
        for bias in [DateCalculationBias.Exact.v, DateCalculationBias.StartOfDay.v, DateCalculationBias.EndOfDay.v]:
            with self.assertRaises(AssertionError):
                self._callFUT(
                    order,
                    base_type=DateCalculationBase.Absolute.v,
                    bias=bias,
                    period=1,
                    abs_date=datetime(1970, 6, 1, 0, 0, 0)
                    )
            try:
                self.assertEqual(
                    self._callFUT(
                        order,
                        base_type=DateCalculationBase.Absolute.v,
                        bias=bias,
                        period=None,
                        abs_date=datetime(1970, 6, 1, 0, 0, 0)
                        ),
                    datetime(1970, 6, 1, 0, 0, 0)
                    )
                self.assertTrue(True)
            except:
                self.fail()
            try:
                self.assertEqual(
                    self._callFUT(
                        order,
                        base_type=DateCalculationBase.Absolute.v,
                        bias=bias,
                        period=0,
                        abs_date=datetime(1970, 6, 1, 0, 0, 0)
                        ),
                    datetime(1970, 6, 1, 0, 0, 0)
                    )
            except:
                self.fail()

    def test_relative_order_date(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        order = testing.DummyModel(
            sales_segment=testing.DummyModel(
                performance=testing.DummyModel()
                ),
            created_at=datetime(1970, 1, 1, 0, 1, 2)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.OrderDate.v,
                bias=DateCalculationBias.Exact.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 1, 2, 0, 1, 2)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.OrderDate.v,
                bias=DateCalculationBias.StartOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 1, 2, 0, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.OrderDate.v,
                bias=DateCalculationBias.EndOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 1, 2, 23, 59, 59)
            )

    def test_relative_performance_start_date(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        performance = testing.DummyModel(start_on=datetime(1970, 8, 1, 19, 0, 0))
        order = testing.DummyModel(
            sales_segment=testing.DummyModel(performance=performance),
            created_at=datetime(1970, 1, 1, 0, 1, 2),
            performance=performance,
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceStartDate.v,
                bias=DateCalculationBias.Exact.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 2, 19, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceStartDate.v,
                bias=DateCalculationBias.StartOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 2, 0, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceStartDate.v,
                bias=DateCalculationBias.EndOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 2, 23, 59, 59)
            )

    def test_relative_performance_end_date(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        performance = testing.DummyModel(end_on=datetime(1970, 8, 5, 18, 0, 0))
        order = testing.DummyModel(
            performance=performance,
            sales_segment=testing.DummyModel(performance=performance),
            created_at=datetime(1970, 1, 1, 0, 1, 2)
            )

        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceEndDate.v,
                bias=DateCalculationBias.Exact.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 6, 18, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceEndDate.v,
                bias=DateCalculationBias.StartOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 6, 0, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.PerformanceEndDate.v,
                bias=DateCalculationBias.EndOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 8, 6, 23, 59, 59)
            )

    def test_relative_sales_start_date(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        order = testing.DummyModel(
            sales_segment=testing.DummyModel(
                performance=testing.DummyModel(
                    ),
                start_at=datetime(1970, 2, 1, 0, 0, 1)
                ),
            created_at=datetime(1970, 1, 1, 0, 1, 2)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesStartDate.v,
                bias=DateCalculationBias.Exact.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 2, 2, 0, 0, 1)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesStartDate.v,
                bias=DateCalculationBias.StartOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 2, 2, 0, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesStartDate.v,
                bias=DateCalculationBias.EndOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 2, 2, 23, 59, 59)
            )

    def test_relative_sales_end_date(self):
        from .models import DateCalculationBase, DateCalculationBias
        from datetime import datetime
        order = testing.DummyModel(
            sales_segment=testing.DummyModel(
                performance=testing.DummyModel(
                    ),
                end_at=datetime(1970, 3, 31, 23, 59, 58)
                ),
            created_at=datetime(1970, 1, 1, 0, 1, 2)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesEndDate.v,
                bias=DateCalculationBias.Exact.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 4, 1, 23, 59, 58)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesEndDate.v,
                bias=DateCalculationBias.StartOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 4, 1, 0, 0, 0)
            )
        self.assertEqual(
            self._callFUT(
                order,
                base_type=DateCalculationBase.SalesEndDate.v,
                bias=DateCalculationBias.EndOfDay.v,
                period=1,
                abs_date=datetime(1970, 6, 1, 0, 0, 0)
                ),
            datetime(1970, 4, 1, 23, 59, 59)
            )

class SendCMSFeatureTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.cart.models",
            ])
        from .models import Organization, Event, SalesSegmentKindEnum, SalesSegmentGroup, SalesSegment, Performance
        from datetime import datetime
        now = datetime.now()
        event = Event(organization=Organization(short_name='XX'))
        performance = Performance(
           event=event,
           start_on=datetime(2014, 1, 1, 0, 0, 0)
           )
        event.sales_segment_groups=[
            SalesSegmentGroup(
                kind='normal',
                sales_segments=[
                    SalesSegment(performance=performance),
                    SalesSegment(performance=performance, deleted_at=now),
                    ]
                ),
            SalesSegmentGroup(
                deleted_at=now,
                kind='vip',
                sales_segments=[
                    SalesSegment(performance=performance),
                    SalesSegment(performance=performance, deleted_at=now),
                    ]
                )
            ]
        self.session.add(event)
        self.session.flush()
        self.event = event

    def tearDown(self):
        _teardown_db()

    def testEvent(self):
        x = self.event.get_cms_data()
        self.assertEqual(len(x['performances'][0]['sales']), 4)


class TicketPrintQueueEntryTest(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        self.session = _setup_db(
            [
                "altair.app.ticketing.orders.models",
                "altair.app.ticketing.core.models",
                "altair.app.ticketing.users.models",
                "altair.app.ticketing.cart.models",
            ])
        from altair.app.ticketing.cart.models import CartSetting
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.operators.models import Operator
        self.cart_setting = CartSetting()
        self.session.add(self.cart_setting)
        CoreTestMixin.setUp(self)
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.session.add(self.sales_segment_group)
        self.sales_segment = SalesSegment(sales_segment_group=self.sales_segment_group)
        self.session.add(self.sales_segment)
        self.stock_types = self._create_stock_types(4)
        self.stocks = self._create_stocks(self.stock_types)
        self.products = self._create_products(self.stocks, sales_segment=self.sales_segment)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(sales_segment_group=self.sales_segment_group)
        self.operator = Operator()

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .models import TicketPrintQueueEntry
        return TicketPrintQueueEntry

    def test_regression_9471(self):
        target = self._getTarget()
        from altair.app.ticketing.core.models import Ticket
        pdmp = self.payment_delivery_method_pairs[0]
        ticket = Ticket(
            ticket_format=self._create_ticket_format(delivery_methods=[pdmp.delivery_method])
            )
        orders = [self._create_order([(self.products[0], 1)], self.sales_segment, pdmp=pdmp) for i in range(4)]
        entries = []
        for order in orders:
            for item in order.items:
                for element in item.elements:
                    entry = target.enqueue(
                        operator=self.operator,
                        ticket=ticket,
                        data={},
                        summary='summary',
                        ordered_product_item=element
                        )
                    entries.append(entry)
        result = target.dequeue([entry.id for entry in entries])
        self.assertEqual(set(result), set(entries))
