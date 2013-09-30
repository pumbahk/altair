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
    from ..models import SejNotification, SejNotificationType
    return SejNotification(
        notification_type=SejNotificationType.TicketingExpire.v,
        process_number=generate_process_number(),
        shop_id=shop_id,
        order_id=sej_order.order_id,
        payment_type=sej_order.payment_type,
        ticketing_due_at=sej_order.ticketing_due_at,
        billing_number=sej_order.billing_number,
        exchange_number=sej_order.exchange_number,
        processed_at=datetime.now()
        )

def create_payment_notification_from_order(shop_id, sej_order):
    from ..models import SejNotification, SejNotificationType
    return SejNotification(
        notification_type=SejNotificationType.PaymentComplete.v,
        process_number=generate_process_number(),
        shop_id=shop_id,
        order_id=sej_order.order_id,
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


class SejNotificationTest(unittest.TestCase, CoreTestMixin):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models'
            ])
        CoreTestMixin.setUp(self)
        self.products = self._create_products(self._create_stocks(self._create_stock_types(5)))

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def last_notification(self):
        from ..models import SejNotification
        return self.session.query(SejNotification).order_by('created_at DESC').first()

    def test_payment_complete_cash_on_delivery(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.CashOnDelivery.v
            )
        self.session.add(sej_order)
        self.session.flush()
        notification = create_payment_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.pay_at is not None
        assert sej_order.issue_at is not None
        assert order.paid_at is not None
        assert order.issued
        assert order.issued_at is not None
        assert order.printed_at is not None
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_payment_complete_prepayment(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number=None,
            billing_number='000000000000',
            payment_type=SejPaymentType.Prepayment.v
            )
        self.session.add(sej_order)
        self.session.flush()
        # 支払
        notification = create_payment_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.pay_at is not None
        assert sej_order.issue_at is None
        assert order.paid_at is not None
        assert order.issued == False
        assert order.issued_at is None
        assert order.printed_at is None
        assert not any(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert not any(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

        # 発券
        sej_order.exchange_number=u'000000000000'
        notification = create_payment_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.pay_at is not None
        assert sej_order.issue_at is not None
        assert order.paid_at is not None
        assert order.issued
        assert order.issued_at is not None
        assert order.printed_at is not None
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_payment_complete_paid_issuing(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Paid.v
            )
        self.session.add(sej_order)
        self.session.flush()
        notification = create_payment_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.issue_at is not None
        assert order.issued
        assert order.issued_at is not None
        assert order.printed_at is not None
        assert all(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert all(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_payment_complete_prepayment_only(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number=None,
            billing_number='000000000000',
            payment_type=SejPaymentType.PrepaymentOnly.v
            )
        self.session.add(sej_order)
        self.session.flush()
        notification = create_payment_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.pay_at is not None
        assert sej_order.issue_at is None
        assert order.paid_at is not None
        assert order.issued == False
        assert order.issued_at is None
        assert order.printed_at is None
        assert not any(ordered_product_item.issued_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)
        assert not any(ordered_product_item.printed_at is not None for ordered_product in order.items for ordered_product_item in ordered_product.ordered_product_items)

    def test_cancel(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.CashOnDelivery.v
            )
        self.session.add(sej_order)
        self.session.flush()
        notification = create_expire_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert order.canceled_at is not None
        assert sej_order.cancel_at is not None

    def test_expire_notification_paid_order(self):
        from ..models import SejOrder, SejPaymentType
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        from altair.app.ticketing.payments.plugins import SEJ_PAYMENT_PLUGIN_ID, SEJ_DELIVERY_PLUGIN_ID
        order = self._create_order(
            [(product, 1) for product in self.products],
            pdmp=PaymentDeliveryMethodPair(
                system_fee=0.,
                transaction_fee=0.,
                delivery_fee=0.,
                discount=0.,
                discount_unit=0,
                public=True,
                payment_method=self.payment_methods[SEJ_PAYMENT_PLUGIN_ID],
                delivery_method=self.delivery_methods[SEJ_DELIVERY_PLUGIN_ID]
                )
            )
        order.order_no = '012301230123'
        self.session.add(order)
        sej_order = SejOrder(
            order_id=order.order_no,
            exchange_number='000000000000',
            billing_number='000000000000',
            payment_type=SejPaymentType.Paid.v
            )
        self.session.add(sej_order)
        self.session.flush()
        notification = create_expire_notification_from_order('000000', sej_order)
        self.session.add(notification)
        from ..notification import process_notification
        process_notification(testing.DummyRequest())
        assert notification.reflected_at is not None
        assert sej_order.processed_at is not None
        assert sej_order.cancel_at is None
        assert order.canceled_at is None
