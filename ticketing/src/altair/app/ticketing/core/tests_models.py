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

    def test_auth3d_notice_setter(self):
        target = self._makeOne(auth3d_notice=u"aa")
        self.assertEqual(target.auth3d_notice, u"aa")
        self.assertEqual(target.x_auth3d_notice, u"aa")

    def test_auth3d_notice_without_acquire(self):
        from .models import SalesSegmentGroup
        target = self._makeOne(auth3d_notice=u"aa",
                               sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
        self.assertEqual(target.auth3d_notice, u"aa")
        self.assertEqual(target.x_auth3d_notice, u"aa")

    def test_auth3d_notice_acquire(self):
        from .models import SalesSegmentGroup
        target = self._makeOne(auth3d_notice=None,
                               sales_segment_group=SalesSegmentGroup(auth3d_notice=u"bb"))
        self.assertEqual(target.auth3d_notice, u"bb")
        self.assertIsNone(target.x_auth3d_notice)

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
