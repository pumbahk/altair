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
        from altair.app.ticketing.sej import models as sej_models
        from altair.app.ticketing.sej.api import remove_default_session
        from altair.app.ticketing.sej.userside_interfaces import ISejTenantLookup
        remove_default_session()
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.checkout.models',
            ])
        self.sej_session = sej_models._session
        from altair.app.ticketing.core.models import SalesSegmentGroup, OrganizationSetting

        self.config = testing.setUp(settings={
            'altair.sej.template_file': ''
            })
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.config.registry.registerUtility(lambda request, organization_id: sej_models.ThinSejTenant(), ISejTenantLookup) # 強引に上書きしている
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
        patch = mock.patch('altair.app.ticketing.payments.plugins.sej.refund_order')
        patches.append(patch)
        self.sej_refund_order = patch.start()
        patch = mock.patch('altair.app.ticketing.payments.plugins.multicheckout.get_multicheckout_3d_api')
        patches.append(patch)
        self.multicheckout_get_multicheckout_3d_api = patch.start()
        self.multicheckout_get_multicheckout_3d_api.return_value.checkout_sales_part_cancel.return_value = mock.Mock(
            CmnErrorCd = '000000',
            CardErrorCd = '000000'
            )
        patch = mock.patch('altair.app.ticketing.checkout.api.get_checkout_service')
        patches.append(patch)
        self.checkout_get_checkout_service = patch.start()
        self.patches = patches
        self.session.flush()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        from altair.app.ticketing.sej.api import remove_default_session
        remove_default_session()
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from altair.app.ticketing.orders.models import Order
        return Order

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.payments import plugins as p
        from altair.app.ticketing.cart.models import Cart, CartSetting
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
            cart_setting=CartSetting(),
            performance=performance,
            payment_delivery_pair=retval.payment_delivery_pair,
            _order_no=retval.order_no
            )
        self.session.add(cart)
        retval.cart = cart
        retval.cart_setting = cart.cart_setting
        retval.performance = performance
        if retval.payment_delivery_pair.payment_method.payment_plugin_id == p.CHECKOUT_PAYMENT_PLUGIN_ID:
            from altair.app.ticketing.checkout.models import Checkout
            self.session.flush()
            self.session.add(Checkout(orderId=retval.order_no, orderCartId=cart.id, orderControlId='0123456'))
        payment_plugin_is_sej = retval.payment_delivery_pair.payment_method.payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID
        delivery_plugin_is_sej = retval.payment_delivery_pair.delivery_method.delivery_plugin_id == p.SEJ_DELIVERY_PLUGIN_ID
        if payment_plugin_is_sej or delivery_plugin_is_sej:
            from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejPaymentType
            if payment_plugin_is_sej:
                if delivery_plugin_is_sej:
                    payment_type = SejPaymentType.CashOnDelivery.v
                else:
                    payment_type = SejPaymentType.PrepaymentOnly.v
            else:
                payment_type = SejPaymentType.Paid.v

            ticket = SejTicket(order_no=retval.order_no)
            self.sej_session.add(ticket)
            sej_order = SejOrder(order_no=retval.order_no, payment_type=payment_type, tickets=[ticket], order_at=datetime(2014, 1, 1, 0, 0, 0))
            ticket.order = sej_order
            self.sej_session.add(sej_order)
        self.sej_session.commit()
        self.session.flush()
        return retval

    def _create_payment_delivery_method_pair(self, payment_plugin_id, delivery_plugin_id):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, DateCalculationBase
        retval = PaymentDeliveryMethodPair(
            sales_segment_group=self.sales_segment_group,
            system_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            transaction_fee=0,
            discount=0,
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
            payment_method=PaymentMethod(payment_plugin_id=payment_plugin_id, fee=0),
            delivery_method=DeliveryMethod(delivery_plugin_id=delivery_plugin_id, fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0)
            )
        self.session.add(retval)
        return retval

    def test_cancel_unpaid(self):
        request = testing.DummyRequest()
        for pn, payment_plugin_id in self.payment_plugins.items():
            if pn in ('multicheckout', 'checkout'):
                continue
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
                self.multicheckout_get_multicheckout_3d_api.return_value.checkout_inquiry.return_value = mock.Mock(
                    CmnErrorCd='001002',
                    CardErrorCd='000000',
                    Status='',
                    )
                target.cancel(request)
                self.assertTrue(target.is_canceled(), description)

    def test_cancel_paid(self):
        from datetime import datetime
        from altair.multicheckout.models import MultiCheckoutStatusEnum
        from altair.app.ticketing.payments import plugins as p
        from .exceptions import OrderCancellationError

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
                self.multicheckout_get_multicheckout_3d_api.return_value.checkout_inquiry.return_value = mock.Mock(
                    CmnErrorCd='000000',
                    CardErrorCd='000000',
                    Status=str(MultiCheckoutStatusEnum.Settled),
                    SalesAmount=target.total_amount
                    )
                if payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID:
                    self.assertFalse(target.cancel(request))
                else:
                    target.cancel(request)
                    self.assertTrue(target.is_canceled(), description)

    def test_cancel_paid_refund_cvs(self):
        from datetime import datetime
        from altair.multicheckout.models import MultiCheckoutStatusEnum
        from altair.app.ticketing.payments import plugins as p
        from altair.app.ticketing.core.models import PaymentMethod
        request = testing.DummyRequest()
        dn = 'sej'
        delivery_plugin_id = self.delivery_plugins[dn]
        sej_payment_method = PaymentMethod(payment_plugin_id=p.SEJ_PAYMENT_PLUGIN_ID)
        for pn, payment_plugin_id in self.payment_plugins.items():
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
            self.assertEqual(target.payment_status, 'refunding', description)
            self.multicheckout_get_multicheckout_3d_api.return_value.checkout_inquiry.return_value = mock.Mock(
                CmnErrorCd='000000',
                CardErrorCd='000000',
                Status=str(MultiCheckoutStatusEnum.Settled),
                SalesAmount=target.total_amount
                )
            target.cancel(request, payment_method=sej_payment_method)
            self.assertEqual(target.payment_status, 'refunded', description)
            self.assertTrue(self.sej_refund_order.called, description)

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
            cart_setting=c_models.CartSetting(),
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

    def test_cancel_refund_anshin_checkout_not_marked_as_refunding(self):
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
                refund_total_amount=300,
                refund_system_fee=100,
                refund_delivery_fee=100,
                paid_at=datetime(2014, 1, 1)
                )
            target.cancel(request)
            self.assertFalse(self.checkout_get_checkout_service.return_value.request_change_order.called)
            self.assertTrue(self.checkout_get_checkout_service.return_value.request_cancel_order.called)
            self.assertEqual(target.payment_status, 'refunded', '%s: %s' % (description, target.payment_status))

    def test_cancel_refund_anshin_checkout_marked_as_refunding(self):
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
                refund=Refund(
                    start_at=datetime(2014, 1, 1),
                    end_at=datetime(2014, 2, 1)
                    ),
                refund_total_amount=300,
                refund_system_fee=100,
                refund_delivery_fee=100,
                paid_at=datetime(2014, 1, 1)
                )
            self.session.add(target)
            self.session.flush()
            target.cancel(request)
            self.assertTrue(self.checkout_get_checkout_service.return_value.request_change_order.called)
            self.assertFalse(self.checkout_get_checkout_service.return_value.request_cancel_order.called)
            self.assertEqual(target.payment_status, 'refunded', description)


    def test_cancel_sej_cancel_unpaid(self):
        from datetime import datetime
        from altair.app.ticketing.payments import plugins as p
        from .models import Refund
        request = testing.DummyRequest()
        pn = 'sej'
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
                paid_at=None
                )
            self.multicheckout_get_multicheckout_3d_api.return_value.checkout_inquiry.return_value = mock.Mock(
                CmnErrorCd='000000',
                SalesAmount=target.total_amount
                )
            target.cancel(request)
            self.assertTrue(self.sej_cancel_sej_order.called)
            self.assertEqual(target.payment_status, 'unpaid', description)

    def _make_order(self, order_no, branch_no, id=None, **kwargs):
        from altair.app.ticketing.orders.models import  Order
        return Order(
            id=id,
            order_no=order_no,
            branch_no=branch_no,
            total_amount=0,
            transaction_fee=0,
            delivery_fee=0,
            system_fee=0,
            special_fee=0,
            **kwargs
            )

    def test_create_order_and_notification(self):
        order = self._make_order(id=1, order_no='a', branch_no=1)
        self.session.add(order)
        self.session.flush()
        self.assertTrue(order.order_notification)


    def test_clone(self):
        from sqlalchemy import desc
        from altair.app.ticketing.orders.models import Order

        order = self._make_order(id=1, order_no='a', branch_no=1)
        self.session.add(order)
        self.session.flush()

        old_order = Order.query.order_by(desc(Order.id)).first()
        new_order = Order.clone(order, deep=True)

        self.assertTrue(new_order.order_notification)
        new_notification = new_order.order_notification

        if old_order.order_notification:
            old_notification = old_order.order_notification
            self.assertEqual(old_notification.sej_remind_at, new_notification.sej_remind_at)
        self.assertEqual(new_order.id, new_notification.order_id)


class ProtoOrderTests(unittest.TestCase, CoreTestMixin):
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
        from altair.app.ticketing.sej import models as sej_models
        from altair.app.ticketing.sej.api import remove_default_session
        from altair.app.ticketing.sej.userside_interfaces import ISejTenantLookup
        remove_default_session()
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.checkout.models',
            ])
        self.sej_session = sej_models._session
        from altair.app.ticketing.core.models import SalesSegmentGroup, OrganizationSetting

        self.config = testing.setUp(settings={
            'altair.sej.template_file': ''
            })
        self.config.include('altair.pyramid_dynamic_renderer')
        self.config.include('altair.app.ticketing.payments')
        self.config.include('altair.app.ticketing.payments.plugins')
        self.config.registry.registerUtility(lambda request, organization_id: sej_models.ThinSejTenant(), ISejTenantLookup) # 強引に上書きしている
        CoreTestMixin.setUp(self)
        self.stock_types = self._create_stock_types(1)
        self.stocks = self._create_stocks(self.stock_types)
        self.product = self._create_products(self.stocks)[0]
        self.session.add(OrganizationSetting(organization=self.organization, multicheckout_shop_name='XX'))
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.session.add(self.sales_segment_group)
        self.order_no_seq = 0
        self.session.flush()

    def tearDown(self):
        _teardown_db()
        testing.tearDown()

    def _getTarget(self):
        from altair.app.ticketing.orders.models import ProtoOrder
        return ProtoOrder

    def _create_order(self, *args, **kwargs):
        from altair.app.ticketing.payments import plugins as p
        from altair.app.ticketing.cart.models import Cart, CartSetting
        from altair.app.ticketing.orders.models import Order, OrderedProduct, OrderedProductItem
        from .models import Performance
        from datetime import datetime
        retval = Order(*args, **kwargs)
        retval.order_no = self._next_order_no()
        retval.items = [
            OrderedProduct(
                price=1,
                product=self.product,
                quantity=2,
                elements=[OrderedProductItem(price=1, quantity=2, product_item=self.product.items[0], attributes=dict(aaa='bbb'))]
                )
            ]
        performance = Performance(
            name='performance',
            code='code',
            start_on=datetime(2014, 1, 1)
            )
        self.session.add(performance)
        cart = Cart(
            cart_setting=CartSetting(),
            performance=performance,
            payment_delivery_pair=retval.payment_delivery_pair,
            _order_no=retval.order_no
            )
        self.session.add(cart)
        retval.cart = cart
        retval.cart_setting = cart.cart_setting
        retval.performance = performance
        if retval.payment_delivery_pair.payment_method.payment_plugin_id == p.CHECKOUT_PAYMENT_PLUGIN_ID:
            from altair.app.ticketing.checkout.models import Checkout
            self.session.flush()
            self.session.add(Checkout(orderId=retval.order_no, orderCartId=cart.id, orderControlId='0123456'))
        payment_plugin_is_sej = retval.payment_delivery_pair.payment_method.payment_plugin_id == p.SEJ_PAYMENT_PLUGIN_ID
        delivery_plugin_is_sej = retval.payment_delivery_pair.delivery_method.delivery_plugin_id == p.SEJ_DELIVERY_PLUGIN_ID
        if payment_plugin_is_sej or delivery_plugin_is_sej:
            from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejPaymentType
            if payment_plugin_is_sej:
                if delivery_plugin_is_sej:
                    payment_type = SejPaymentType.CashOnDelivery.v
                else:
                    payment_type = SejPaymentType.PrepaymentOnly.v
            else:
                payment_type = SejPaymentType.Paid.v

            ticket = SejTicket(order_no=retval.order_no)
            self.sej_session.add(ticket)
            sej_order = SejOrder(order_no=retval.order_no, payment_type=payment_type, tickets=[ticket])
            ticket.order = sej_order
            self.sej_session.add(sej_order)
        self.sej_session.commit()
        self.session.flush()
        return retval

    def _create_payment_delivery_method_pair(self, payment_plugin_id, delivery_plugin_id):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, DateCalculationBase
        retval = PaymentDeliveryMethodPair(
            sales_segment_group=self.sales_segment_group,
            system_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            transaction_fee=0,
            discount=0,
            payment_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_start_in_days=0,
            payment_due_day_calculation_base=DateCalculationBase.OrderDate.v,
            payment_period_days=3,
            issuing_start_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_interval_days=5,
            issuing_end_day_calculation_base=DateCalculationBase.OrderDate.v,
            issuing_end_in_days=364,
            payment_method=PaymentMethod(payment_plugin_id=payment_plugin_id, fee=0),
            delivery_method=DeliveryMethod(delivery_plugin_id=delivery_plugin_id, fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0)
            )
        self.session.add(retval)
        return retval

    def test_create_from_order_like(self):
        order = self._create_order(
            total_amount=1,
            system_fee=1,
            transaction_fee=2,
            delivery_fee=3,
            special_fee=4,
            special_fee_name=u'aaa',
            payment_delivery_pair=self._create_payment_delivery_method_pair(self.payment_plugins['multicheckout'], self.delivery_plugins['sej']),
            attributes=dict(
                ccc='ddd'
                )
            )
        proto_order = self._getTarget().create_from_order_like(order)

        attributes = [
            'order_no',
            'total_amount',
            'shipping_address',
            'payment_delivery_pair',
            'system_fee',
            'special_fee_name',
            'special_fee',
            'transaction_fee',
            'delivery_fee',
            'performance',
            'sales_segment',
            'organization_id',
            'operator',
            'user',
            'issuing_start_at',
            'issuing_end_at',
            'payment_due_at',
            'note',
            'cart_setting_id',
            ]
        for k in attributes:
            self.assertEqual(getattr(proto_order, k), getattr(order, k), k)

        self.assertEqual(dict(proto_order.attributes), dict(order.attributes))
        proto_order_items = sorted(proto_order.items, key=lambda i: i.product_id)
        order_items = sorted(order.items, key=lambda i: i.product_id)
        self.assertEqual(len(proto_order_items), len(order_items))
        for proto_order_item, order_item in zip(proto_order_items, order_items):
            self.assertEqual(proto_order_item.price, order_item.price)
            self.assertEqual(proto_order_item.quantity, order_item.quantity)
            self.assertEqual(proto_order_item.product, order_item.product)
            proto_order_elements = sorted(proto_order_item.elements, key=lambda e: e.product_item_id)
            order_elements = sorted(order_item.elements, key=lambda e: e.product_item_id)
            self.assertEqual(len(proto_order_elements), len(order_elements))
            for proto_order_element, order_element in zip(proto_order_elements, order_elements):
                self.assertEqual(proto_order_element.price, order_element.price)
                self.assertEqual(proto_order_element.quantity, order_element.quantity)
                self.assertEqual(proto_order_element.product_item, order_element.product_item)
                self.assertEqual(dict(proto_order_element.attributes), dict(order_element.attributes))

