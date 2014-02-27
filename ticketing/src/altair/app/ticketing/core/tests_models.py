import unittest
import mock
from altair.app.ticketing.testing import _setup_db, _teardown_db
from pyramid import testing
from .testing import CoreTestMixin

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

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import Order
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
                sales_segment=target,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            orders.append(order)

        others = []
        for i in range(2):
            order = Order(
                user=other,
                sales_segment=target,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            others.append(order)

        cancels = []
        for i in range(2):
            order = Order(
                user=user,
                sales_segment=target,
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
        from altair.app.ticketing.core.models import Order, ShippingAddress
        from altair.app.ticketing.cart.models import Cart
        from datetime import datetime

        target = self._makeOne()

        mail_addr  = 'testing@example.com'
        mail_addr_other = 'other@example.com'

        orders = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=target,
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)
        
        for i in range(2):
            shipping_address = ShippingAddress(email_2=mail_addr)
            order = Order(
                sales_segment=target,
                shipping_address=shipping_address,
                total_amount=0,
                system_fee=0, transaction_fee=0, delivery_fee=0)
            self.session.add(order)
            orders.append(order)

        cancels = []
        for i in range(2):
            shipping_address = ShippingAddress(email_1=mail_addr)
            order = Order(
                sales_segment=target,
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
                sales_segment=target,
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


class PerformanceTests(unittest.TestCase):
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
        from .models import Performance
        return Performance

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import Order, SalesSegment
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
        from altair.app.ticketing.core.models import Order, ShippingAddress, SalesSegment
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

    def test_query_orders_by_user(self):
        from altair.app.ticketing.core.models import Order, SalesSegment
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
        from altair.app.ticketing.core.models import Order, ShippingAddress, SalesSegment
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


class OrderTests(unittest.TestCase, CoreTestMixin):
    @property 
    def payment_plugins(self):
        from altair.app.ticketing.payments import plugins as p
        return {
            'multicheckout': p.MULTICHECKOUT_PAYMENT_PLUGIN_ID,
            'checkout': p.CHECKOUT_PAYMENT_PLUGIN_ID,
            'sej': p.SEJ_PAYMENT_PLUGIN_ID,
            'reserve_number': p.RESERVE_NUMBER_PAYMENT_PLUGIN_ID,
            }

    @property
    def delivery_plugins(self):
        from altair.app.ticketing.payments import plugins as p
        return {
            'shipping': p.SHIPPING_DELIVERY_PLUGIN_ID,
            'sej': p.SEJ_DELIVERY_PLUGIN_ID,
            'reserve_number': p.RESERVE_NUMBER_DELIVERY_PLUGIN_ID,
            'qr': p.QR_DELIVERY_PLUGIN_ID,
            'orion': p.ORION_DELIVERY_PLUGIN_ID,
            }

    def _next_order_no(self):
        self.order_no_seq += 1
        return 'XX%010d' % self.order_no_seq

    def setUp(self):
        self.config = testing.setUp(settings={
            'altair.sej.template_file': ''
            })
        self.config.include('altair.app.ticketing.renderers')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.session = _setup_db(['altair.app.ticketing.core.models'])
        from .models import SalesSegmentGroup, OrganizationSetting
        CoreTestMixin.setUp(self)
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.product = self._create_products(self.stocks)[0]
        self.session.add(OrganizationSetting(organization=self.organization, multicheckout_shop_name='XX'))
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.session.add(self.sales_segment_group)
        from altair.app.ticketing.checkout.models import RakutenCheckoutSetting
        self.session.add(RakutenCheckoutSetting(organization_id=self.organization.id, channel=1))
        self.order_no_seq = 0
        patches = []
        patch = mock.patch('altair.app.ticketing.checkout.api.Checkout.request_cancel_order')
        patches.append(patch)
        self.checkout_request_cancel_order = patch.start()
        patch = mock.patch('altair.app.ticketing.sej.api.cancel_sej_order')
        patches.append(patch)
        self.sej_cancel_sej_order = patch.start()
        patch = mock.patch('altair.app.ticketing.sej.api.refund_sej_order')
        patches.append(patch)
        self.sej_refund_sej_order = patch.start()
        patch = mock.patch('altair.multicheckout.api.get_multicheckout_3d_api')
        patches.append(patch)
        self.multicheckout_get_multicheckout_3d_api = patch.start()
        self.multicheckout_get_multicheckout_3d_api.return_value.checkout_sales_part_cancel.return_value.CmnErrorCd = '000000'
        self.multicheckout_get_multicheckout_3d_api.return_value.checkout_sales_part_cancel.return_value.CardErrorCd = '000000'
        self.patches = patches
        self.session.flush()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from .models import Order
        return Order

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.payments import plugins as p
        from altair.app.ticketing.cart.models import Cart
        from .models import OrderedProduct, OrderedProductItem
        retval = self._getTarget()(*args, **kwargs)
        retval.order_no = self._next_order_no()
        retval.items = [
            OrderedProduct(
                price=1,
                product=self.product,
                elements=[OrderedProductItem(price=1, product_item=self.product.items[0])]
                )
            ]
        cart = Cart(
            payment_delivery_pair=retval.payment_delivery_pair,
            _order_no=retval.order_no
            )
        self.session.add(cart)
        retval.cart = cart
        if retval.payment_delivery_pair.payment_method.payment_plugin_id == p.CHECKOUT_PAYMENT_PLUGIN_ID:
            from altair.app.ticketing.checkout.models import Checkout
            self.session.flush()
            self.session.add(Checkout(orderId=retval.order_no, orderCartId=cart.id, orderControlId='0123456'))
        if retval.payment_delivery_pair.payment_method.payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID or \
           retval.payment_delivery_pair.delivery_method.delivery_plugin_id == p.SEJ_DELIVERY_PLUGIN_ID:
            from altair.app.ticketing.sej.models import SejOrder, SejTicket
            ticket = SejTicket(order_no=retval.order_no)
            self.session.add(ticket)
            sej_order = SejOrder(order_no=retval.order_no, tickets=[ticket])
            ticket.order = sej_order
            self.session.add(sej_order)
        self.session.flush()
        return retval

    def _create_payment_delivery_method_pair(self, payment_plugin_id, delivery_plugin_id):
        from .models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod
        retval = PaymentDeliveryMethodPair(
            sales_segment_group=self.sales_segment_group,
            system_fee=0,
            delivery_fee=0,
            transaction_fee=0,
            discount=0,
            payment_method=PaymentMethod(payment_plugin_id=payment_plugin_id, fee=0),
            delivery_method=DeliveryMethod(delivery_plugin_id=delivery_plugin_id, fee=0)
            )
        self.session.add(retval)
        return retval

    def test_cancel_unpaid(self):
        request = testing.DummyRequest()
        for pn, payment_plugin_id in self.payment_plugins.items():
            for dn, delivery_plugin_id in self.delivery_plugins.items():
                description = 'payment_plugin=%s, delivery_plugin=%s' % (pn, dn)
                payment_delivery_method_pair = self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id)
                target = self._makeOne(
                    organization_id=self.organization.id,
                    payment_delivery_pair=payment_delivery_method_pair,
                    total_amount=0,
                    system_fee=0,
                    transaction_fee=0,
                    delivery_fee=0
                    )
                target.cancel(request)
                self.assertTrue(target.is_canceled(), description)

    def test_cancel_paid(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins as p
        request = testing.DummyRequest()
        for pn, payment_plugin_id in self.payment_plugins.items():
            for dn, delivery_plugin_id in self.delivery_plugins.items():
                description = 'payment_plugin=%s, delivery_plugin=%s' % (pn, dn)
                payment_delivery_method_pair = self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id)
                target = self._makeOne(
                    organization_id=self.organization.id,
                    payment_delivery_pair=payment_delivery_method_pair,
                    total_amount=0,
                    system_fee=0,
                    transaction_fee=0,
                    delivery_fee=0,
                    paid_at=datetime(2014, 1, 1)
                    )
                target.cancel(request)
                if payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID:
                    self.assertTrue(self.sej_refund_sej_order.called)
                self.assertTrue(target.is_canceled(), description)

