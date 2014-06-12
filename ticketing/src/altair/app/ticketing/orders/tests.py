# -*- coding:utf-8 -*-

""" TBA
"""

import unittest
import mock
from pyramid import testing
from altair.app.ticketing.core.testing import CoreTestMixin
from ..testing import _setup_db, _teardown_db

class OrderedProductItemTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.orders.models',
            ],
        )

    @classmethod
    def tearDownClass(cls):
        _teardown_db()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _getTarget(self):
        from .models import OrderedProductItem
        return OrderedProductItem

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _create_seats(self, num):
        from altair.app.ticketing.core.models import Seat, Venue, Site, Organization
        organization = Organization(short_name="testing")
        site = Site()
        venue = Venue(site=site, organization=organization)
        return [Seat(name=u"Seat %d" % i, venue=venue,
                     l0_id="seat-%d" % i) for i in range(num)]

    def _create_seat_statuses(self, seats):
        from altair.app.ticketing.core.models import SeatStatus, SeatStatusEnum
        return [SeatStatus(seat_id=s.id,
                    status=int(SeatStatusEnum.Ordered)) for s in seats]

    def _create_product_item(self):
        from altair.app.ticketing.core.models import ProductItem, Stock, Performance, StockType, StockStatus
        performance = Performance()
        stock = Stock(performance=performance,
                      stock_type=StockType())
        stock_status = StockStatus(stock=stock, quantity=100)
        return ProductItem(stock=stock, price=100.0)

    def test_release(self):
        seats = self._create_seats(4)
        map(self.session.add, seats)
        self.session.flush()
        statuses = self._create_seat_statuses(seats)
        map(self.session.add, statuses)
        product_item = self._create_product_item()
        self.session.add(product_item)
        self.session.flush()

        target = self._makeOne(seats=seats, product_item=product_item,
                               price=product_item.price)

        target.release()
        self._assertStatus(target.seats)

    def _assertStatus(self, seats):
        from altair.app.ticketing.core.models import SeatStatusEnum, SeatStatus
        statuses = self.session.query(SeatStatus).filter(SeatStatus.seat_id.in_([s.id for s in seats]))
        for s in statuses:
            self.assertEqual(s.status, int(SeatStatusEnum.Vacant))


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
        from altair.app.ticketing.sej.models import ThinSejTenant
        from altair.app.ticketing.sej.userside_interfaces import ISejTenantLookup
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.checkout.models',
            ])
        from altair.app.ticketing.core.models import SalesSegmentGroup, OrganizationSetting

        self.config = testing.setUp(settings={
            'altair.sej.template_file': ''
            })
        self.config.include('altair.app.ticketing.renderers')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.config.registry.registerUtility(lambda request, organization_id: ThinSejTenant(), ISejTenantLookup) # 強引に上書きしている
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
        patch = mock.patch('altair.app.ticketing.checkout.api.AnshinCheckoutAPI.request_cancel_order')
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
        patch = mock.patch('altair.app.ticketing.checkout.api.get_checkout_service')
        patches.append(patch)
        self.checkout_get_checkout_service = patch.start()
        self.patches = patches
        self.session.flush()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from altair.app.ticketing.orders.models import Order
        return Order

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.payments import plugins as p
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.orders.models import OrderedProduct, OrderedProductItem
        from .models import Performance
        from datetime import datetime
        retval = self._getTarget()(*args, **kwargs)
        retval.order_no = self._next_order_no()
        retval.items = [
            OrderedProduct(
                price=1,
                product=self.product,
                elements=[OrderedProductItem(price=1, product_item=self.product.items[0])]
                )
            ]
        performance = Performance(
            name='performance',
            code='code',
            start_on=datetime(2014, 1, 1)
            )
        self.session.add(performance)
        cart = Cart(
            performance=performance,
            payment_delivery_pair=retval.payment_delivery_pair,
            _order_no=retval.order_no
            )
        self.session.add(cart)
        retval.cart = cart
        retval.performance = performance
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
                if payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID:
                    from .models import Refund
                    refund = Refund(
                        start_at=datetime(2014, 1, 1),
                        end_at=datetime(2014, 2, 1)
                        )
                    self.session.add(refund)
                    target.refund = refund
                    target = self._getTarget().clone(target)
                    target.refund = refund
                    self.session.add(target)
                    self.session.flush()
                target.cancel(request)
                if payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID:
                    self.assertTrue(self.sej_refund_sej_order.called)
                    self.assertEqual(target.payment_status, 'refunded', description)
                else:
                    self.assertTrue(target.is_canceled(), description)

    def test_payment_status_changable_unpaid_non_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=None
                        )
                    self.assertFalse(target.payment_status_changable('paid'))
                    self.assertTrue(target.payment_status_changable('unpaid'))

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=None
                )
            self.assertTrue(target.payment_status_changable('paid'))
            self.assertTrue(target.payment_status_changable('unpaid'))

    def test_payment_status_changable_unpaid_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        channel=3,
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=None
                        )
                    self.assertFalse(target.payment_status_changable('paid'))
                    self.assertTrue(target.payment_status_changable('unpaid'))

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                channel=3,
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=None
                )
            self.assertTrue(target.payment_status_changable('paid'))
            self.assertTrue(target.payment_status_changable('unpaid'))

    def test_payment_status_changable_paid_non_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=datetime(2014, 1, 1, 0, 0, 0)
                        )
                    self.assertTrue(target.payment_status_changable('paid'))
                    self.assertFalse(target.payment_status_changable('unpaid'))

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=datetime(2014, 1, 1, 0, 0, 0)
                )
            self.assertTrue(target.payment_status_changable('paid'))
            self.assertTrue(target.payment_status_changable('unpaid'))

    def test_payment_status_changable_paid_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        channel=3,
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=datetime(2014, 1, 1, 0, 0, 0)
                        )
                    self.assertTrue(target.payment_status_changable('paid'))
                    self.assertTrue(target.payment_status_changable('unpaid'))

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                channel=3,
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=datetime(2014, 1, 1, 0, 0, 0)
                )
            self.assertTrue(target.payment_status_changable('paid'))
            self.assertTrue(target.payment_status_changable('unpaid'))

    def test_change_payment_status_unpaid_non_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=None
                        )
                    self.assertEqual(target.payment_status, 'unpaid')
                    self.assertFalse(target.change_payment_status('unpaid'))
                    self.assertFalse(target.change_payment_status('paid'))
                    self.assertEqual(target.payment_status, 'unpaid')

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=None
                )
            self.assertEqual(target.payment_status, 'unpaid')
            self.assertFalse(target.change_payment_status('unpaid'))
            self.assertTrue(target.change_payment_status('paid'))
            self.assertEqual(target.payment_status, 'paid')

    def test_change_payment_status_unpaid_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        channel=3,
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=None
                        )
                    self.assertEqual(target.payment_status, 'unpaid')
                    self.assertFalse(target.change_payment_status('paid'))
                    self.assertFalse(target.change_payment_status('paid'))
                    self.assertEqual(target.payment_status, 'unpaid')

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                channel=3,
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=None
                )
            self.assertEqual(target.payment_status, 'unpaid')
            self.assertFalse(target.change_payment_status('unpaid'))
            self.assertTrue(target.change_payment_status('paid'))
            self.assertEqual(target.payment_status, 'paid')

    def test_change_payment_status_paid_non_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=datetime(2014, 1, 1, 0, 0, 0)
                        )
                    self.assertEqual(target.payment_status, 'paid')
                    self.assertFalse(target.change_payment_status('paid'))
                    self.assertFalse(target.change_payment_status('unpaid'))
                    self.assertEqual(target.payment_status, 'paid')

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=datetime(2014, 1, 1, 0, 0, 0)
                )
            self.assertEqual(target.payment_status, 'paid')
            self.assertFalse(target.change_payment_status('paid'))
            self.assertTrue(target.change_payment_status('unpaid'))
            self.assertEqual(target.payment_status, 'unpaid')

    def test_change_payment_status_paid_inner(self):
        from datetime import datetime
        for payment_plugin_id in self.payment_plugins.values():
            if payment_plugin_id != self.payment_plugins['reserve_number']:
                for delivery_plugin_id in self.delivery_plugins.values():
                    target = self._makeOne(
                        channel=3,
                        organization_id=self.organization.id,
                        payment_delivery_pair=self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id),
                        total_amount=0,
                        system_fee=0,
                        transaction_fee=0,
                        delivery_fee=0,
                        paid_at=datetime(2014, 1, 1, 0, 0, 0)
                        )
                    self.assertEqual(target.payment_status, 'paid')
                    self.assertFalse(target.change_payment_status('paid'))
                    self.assertTrue(target.change_payment_status('unpaid'))
                    self.assertEqual(target.payment_status, 'unpaid')

        for delivery_plugin_id in self.delivery_plugins.values():
            target = self._makeOne(
                channel=3,
                organization_id=self.organization.id,
                payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['reserve_number'], delivery_plugin_id),
                total_amount=0,
                system_fee=0,
                transaction_fee=0,
                delivery_fee=0,
                paid_at=datetime(2014, 1, 1, 0, 0, 0)
                )
            self.assertEqual(target.payment_status, 'paid')
            self.assertFalse(target.change_payment_status('paid'))
            self.assertTrue(target.change_payment_status('unpaid'))
            self.assertEqual(target.payment_status, 'unpaid')

    def test_create_from_cart(self):

        from altair.app.ticketing.cart import models as c_models
        from altair.app.ticketing.core import models as core_models
        from decimal import Decimal

        request = testing.DummyRequest()
        seats = self._create_seats([self.stocks[0]])
        cart = c_models.Cart.create(
            request,
            performance=self.performance,
            sales_segment=core_models.SalesSegment(sales_segment_group=self.sales_segment_group),
            payment_delivery_pair=self._create_payment_delivery_method_pair(
                self.payment_plugins['sej'],
                self.delivery_plugins['sej']
                ),
            items=[
                c_models.CartedProduct(
                    elements=[
                        c_models.CartedProductItem(
                            product_item=core_models.ProductItem(price=100.00),
                            seats=seats[0:1]
                            ),
                        ],
                    product=core_models.Product(
                        price=Decimal(100.00),
                        ),
                    quantity=1,
                    ),
                ],
            )

        target = self._getTarget()

        result = target.create_from_cart(cart)

        self.assertIsNotNone(result)
        self.assertEqual(len(result.ordered_products), 1)
        ordered_product = result.ordered_products[0]
        self.assertEqual(ordered_product.price, 100.00)
        self.assertEqual(len(ordered_product.ordered_product_items), 1)
        ordered_product_item = ordered_product.ordered_product_items[0]
        self.assertEqual(ordered_product_item.price, 100.00)
        self.assertEqual(len(ordered_product_item.seats), 1)
        seat = ordered_product_item.seats[0]
        self.assertEqual(seat.id, seats[0].id)

    def test_cancel_refund_anshin_checkout(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins as p
        from .models import Refund
        request = testing.DummyRequest()
        pn = 'checkout'
        payment_plugin_id = self.payment_plugins[pn]
        for dn, delivery_plugin_id in self.delivery_plugins.items():
            description = 'payment_plugin=%s, delivery_plugin=%s' % (pn, dn)
            payment_delivery_method_pair = self._create_payment_delivery_method_pair(payment_plugin_id, delivery_plugin_id)
            target = self._makeOne(
                organization_id=self.organization.id,
                payment_delivery_pair=payment_delivery_method_pair,
                total_amount=500,
                system_fee=200,
                transaction_fee=0,
                delivery_fee=200,
                refund = Refund(
                    start_at=datetime(2014, 1, 1),
                    end_at=datetime(2014, 2, 1)
                    ),
                refund_total_amount=300,
                refund_system_fee=100,
                refund_delivery_fee=100,
                paid_at=datetime(2014, 1, 1)
                )
            target.cancel(request)
            self.assertTrue(self.checkout_get_checkout_service.return_value.request_change_order.called)
            self.assertEqual(target.payment_status, 'refunded', description)
