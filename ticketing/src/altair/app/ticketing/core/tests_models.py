import unittest
from altair.app.ticketing.testing import _setup_db, _teardown_db

class SalesSegmentTests(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db(
            [
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

    # def test_auth3d_notice_setter(self):
    #     target = self._makeOne(auth3d_notice=u"aa")
    #     self.assertEqual(target.auth3d_notice, u"aa")
    #     self.assertEqual(target.x_auth3d_notice, u"aa")

    # def test_auth3d_notice_without_acquire(self):
    #     from .models import SalesSegmentGroup
    #     target = self._makeOne(auth3d_notice=u"aa",
    #                            sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
    #     self.assertEqual(target.auth3d_notice, u"aa")
    #     self.assertEqual(target.x_auth3d_notice, u"aa")

    # def test_auth3d_notice_acquire(self):
    #     from .models import SalesSegmentGroup
    #     target = self._makeOne(auth3d_notice=None,
    #                            sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
    #     self.assertEqual(target.auth3d_notice, u"bb")
    #     self.assertIsNone(target.x_auth3d_notice)

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import Order
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.users.models import User

        target = self._makeOne()

        user = User()
        other = User()
        orders = []
        for i in range(2):
            cart = Cart(sales_segment=target)
            order = Order(user=user, cart=cart,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)

        others = []
        for i in range(2):
            cart = Cart(sales_segment=target)
            order = Order(user=other, cart=cart,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0)
            others.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_user(user).all()

        self.assertEqual(result, orders)

    def test_query_orders_by_mailaddress(self):
        from altair.app.ticketing.core.models import Order, ShippingAddress
        from altair.app.ticketing.cart.models import Cart

        target = self._makeOne()

        orders = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1="testing@example.com")
            cart = Cart(sales_segment=target)
            order = Order(cart=cart,
                          shipping_address=shipping_address,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)
        for i in range(2):
            shipping_address = ShippingAddress(email_2="testing@example.com")
            cart = Cart(sales_segment=target)
            order = Order(cart=cart,
                          shipping_address=shipping_address,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)

        others = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1="other@example.com")
            cart = Cart(sales_segment=target)
            order = Order(cart=cart,
                          shipping_address=shipping_address,
                          total_amount=0,
                          system_fee=0, transaction_fee=0, delivery_fee=0)
            others.append(order)

        self.session.add(target)
        self.session.flush()

        result = target.query_orders_by_mailaddress("testing@example.com").all()

        self.assertEqual(result, orders)


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
