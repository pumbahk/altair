# -*- coding:utf-8 -*-
import unittest
from datetime import datetime
import os
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin

last_process_number = 0

def generate_process_number():
    global last_process_number
    last_process_number += 1
    return last_process_number

def create_expire_notification_from_order(shop_id, sej_order):
    from .models import SejNotification, SejNotificationType
    return SejNotification(
        notification_type=SejNotificationType.TicketingExpire.v,
        process_number=generate_process_number(),
        shop_id=shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        processed_at=datetime.now()
        )

def create_payment_notification_from_order(shop_id, sej_order):
    from .models import SejNotification, SejNotificationType
    return SejNotification(
        notification_type=SejNotificationType.PaymentComplete.v,
        process_number=generate_process_number(),
        shop_id=shop_id,
        order_no=sej_order.order_no,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        total_price=sej_order.total_price,
        ticket_count=sej_order.ticket_count,
        total_ticket_count=sej_order.total_ticket_count,
        pay_store_name=u'テスト店舗',
        pay_store_number=u'000000',
        ticketing_store_name=u'テスト店舗',
        ticketing_store_number=u'000000',
        processed_at=datetime.now()
        )

class SejNotificationProcessorTest(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        from ..api import remove_default_session
        from altair.sqlahelper import register_sessionmaker_with_engine
        remove_default_session()
        from altair.app.ticketing import install_ld
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.lots.models',
            'altair.app.ticketing.sej.models',
            ], hook=install_ld)
        from ..models import _session
        _session.remove()
        self._session =  _session
        CoreTestMixin.setUp(self)
        self.products = self._create_products(self._create_stocks(self._create_stock_types(5)))
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.sej')
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )

    def tearDown(self):
        testing.tearDown()
        from ..api import remove_default_session
        from altair.app.ticketing import uninstall_ld
        remove_default_session()
        _teardown_db()
        uninstall_ld()

    def _getTarget(self):
        from .processor import SejNotificationProcessor
        return SejNotificationProcessor

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def last_notification(self):
        from .models import SejNotification
        return self._session.query(SejNotification).order_by('created_at DESC').first()

    def test_payment_complete_cash_on_delivery(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                special_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.CashOnDelivery.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        notification = create_payment_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.pay_at == notification.processed_at
        assert sej_order.issue_at == notification.processed_at
        assert order.paid_at == notification.processed_at
        assert order.issued
        assert order.issued_at == notification.processed_at
        assert order.printed_at == notification.processed_at
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)

    def test_payment_complete_prepayment_1(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                special_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number=None,
            billing_number='000000000000',
            payment_type=SejPaymentType.Prepayment.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        # 支払
        notification = create_payment_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.pay_at is not None
        assert sej_order.issue_at is None
        assert order.paid_at is not None
        assert order.issued == False
        assert order.issued_at is None
        assert order.printed_at is None
        assert not any(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)
        assert not any(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)

    def test_payment_complete_prepayment_2(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number=u'000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Prepayment.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)

        # 発券
        notification = create_payment_notification_from_order('000000', sej_order)
        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.pay_at != notification.processed_at
        assert sej_order.issue_at == notification.processed_at
        assert order.paid_at != notification.processed_at
        assert order.issued
        assert order.issued_at == notification.processed_at
        assert order.printed_at == notification.processed_at
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_payment_complete_paid_issuing(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Paid.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        notification = create_payment_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.issue_at == notification.processed_at
        assert order.issued
        assert order.issued_at == notification.processed_at
        assert order.printed_at == notification.processed_at
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.elements)

    def test_payment_complete_prepayment_only(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number=None,
            billing_number='000000000000',
            payment_type=SejPaymentType.PrepaymentOnly.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        notification = create_payment_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.pay_at == notification.processed_at
        assert sej_order.issue_at is None
        assert order.paid_at is not None
        assert order.issued == False
        assert order.issued_at is None
        assert order.printed_at is None
        assert not any(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert not any(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_cancel_basic(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        self.session.add(order)
        self.session.flush()
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.CashOnDelivery.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        notification = create_expire_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert order.canceled_at == notification.processed_at
        assert sej_order.cancel_at == notification.processed_at

    def test_cancel_branches(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        self.session.add(order)
        self.session.flush()
        order.order_no = '012301230123'
        sej_orders = [
            SejOrder(
                order_no=order.order_no,
                exchange_number='000000000000',
                billing_number='000000000000',
                payment_type=SejPaymentType.CashOnDelivery.v,
                order_at=datetime(2013, 1, 1, 1, 1, 1),
                branch_no=1
                ),
            SejOrder(
                order_no=order.order_no,
                exchange_number='000000000001',
                billing_number='000000000001',
                payment_type=SejPaymentType.CashOnDelivery.v,
                order_at=datetime(2013, 1, 1, 1, 1, 1),
                branch_no=2
                )
            ]
        for sej_order in sej_orders:
            self._session.add(sej_order)

        notification1 = create_expire_notification_from_order('000000', sej_orders[0])

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_orders[0], order, notification1)

        assert notification1.reflected_at == now
        assert order.canceled_at is None
        assert sej_orders[0].cancel_at == notification1.processed_at
        assert sej_orders[1].cancel_at is None

        notification2 = create_expire_notification_from_order('000000', sej_orders[1])

        now = datetime(2013, 1, 1, 1, 23, 48)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_orders[1], order, notification2)

        assert notification2.reflected_at == now
        assert order.canceled_at == notification2.processed_at
        assert sej_orders[0].cancel_at == notification1.processed_at
        assert sej_orders[1].cancel_at == notification2.processed_at

    def test_cancel_prepayment_unpaid(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        self.session.add(order)
        self.session.flush()
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Prepayment.v,
            branch_no=1
            )
        self._session.add(sej_order)

        notification1 = create_expire_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification1)

        assert notification1.reflected_at == now
        assert order.canceled_at is not None
        assert sej_order.cancel_at is not None

    def test_cancel_prepayment_paid(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        self.session.add(order)
        self.session.flush()
        order.order_no = '012301230123'
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Prepayment.v,
            pay_at=datetime(2013, 1, 1, 0, 0, 0),
            order_at=datetime(2013, 1, 1, 1, 1, 1),
            branch_no=1
            )
        self._session.add(sej_order)

        notification1 = create_expire_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification1)

        assert notification1.reflected_at == now
        assert order.canceled_at is None
        assert sej_order.cancel_at is None

    def test_expire_notification_paid_order(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            sales_segment=None,
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee_per_order=0.,
                delivery_fee_per_principal_ticket=0.,
                delivery_fee_per_subticket=0.,
                discount=0.,
                discount_unit=0,
                special_fee=0.,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        order.paid_at=datetime(2012, 1, 1, 1, 23, 45)
        sej_order = SejOrder(
            order_no=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Paid.v,
            order_at=datetime(2013, 1, 1, 1, 1, 1)
            )
        self._session.add(sej_order)
        notification = create_expire_notification_from_order('000000', sej_order)

        now = datetime(2013, 1, 1, 1, 23, 45)
        processor = self._makeOne(testing.DummyRequest(), now)
        processor(sej_order, order, notification)

        assert notification.reflected_at == now
        assert sej_order.processed_at == notification.processed_at
        assert sej_order.cancel_at is None
        assert order.canceled_at is None
