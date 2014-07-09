# -*- coding:utf-8 -*-
import unittest
import mock
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing
from .testing import CoreTestMixin

class SalesSegmentTests(unittest.TestCase):
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
                payment_delivery_pair=pdmp
                )
            order = Order(user=user, cart=cart,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0,
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
            cart = Cart(sales_segment=target)
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
            cart = Cart(sales_segment=target)
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
            cart = Cart(sales_segment=target)
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
            cart = Cart(sales_segment=target)
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
            cart = Cart(sales_segment=target)
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
            cart = Cart(sales_segment=target)
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
