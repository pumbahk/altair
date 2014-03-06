# -*- coding:utf-8 -*-
import unittest
from datetime import date, datetime

class TokenStatusTests(unittest.TestCase):
    def _getTarget(self):
        from altair.app.ticketing.checkinstation.todict import TokenStatusDictBuilder
        return TokenStatusDictBuilder

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getOrder(self):
        from altair.app.ticketing.core.models import Order, Performance
        return Order(performance=Performance())

    def _getHistory(self):
        from altair.app.ticketing.core.models import TicketPrintHistory, OrderedProductItemToken
        return TicketPrintHistory(item_token=OrderedProductItemToken())

    def test_printed_status__fresh_order__unprinted(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        self.assertTrue(target._is_unprinted_yet(order, history.item_token))

    def test_printed_status__printed_with_order(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.printed_at = datetime(2013, 1, 1, 1, 1, 1)
        self.assertFalse(target._is_unprinted_yet(order, history.item_token))

    def test_printed_status__printed_with_token(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        history.item_token.printed_at = datetime(2013, 1, 1, 1, 1, 1)
        self.assertFalse(target._is_unprinted_yet(order, history.item_token))

    def test_canceled_status__fresh_order__not_canceled(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        self.assertFalse(target._is_canceled(order))

    def test_canceled_status__canceled(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.canceled_at = datetime(2013, 1, 1, 6, 1, 1, 1)
        self.assertTrue(target._is_canceled(order))

    def test_printable_date_status__before_start__failure(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.performance.start_on = datetime(2013, 1, 6, 9)
        today = date(2013, 1, 1)
        self.assertFalse(target._is_printable_date(order, today))

    def test_printable_date_status__same_date__start_on(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.performance.start_on = datetime(2013, 1, 6, 9)
        today = date(2013, 1, 6)
        self.assertTrue(target._is_printable_date(order, today))

    def test_printable_date_status__same_date__open_on(self):
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.performance.open_on = datetime(2013, 1, 6, 9)
        today = date(2013, 1, 6)
        self.assertTrue(target._is_printable_date(order, today))

    def test_printable_date_status__pdmp_issuing_start_at(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.performance.open_on = datetime(2013, 1, 6, 9)
        order.payment_delivery_pair = PaymentDeliveryMethodPair(issuing_start_at=datetime(2012, 1, 1, 9))
        today = date(2013, 1, 1, 9)
        self.assertTrue(target._is_printable_date(order, today))

    def test_supported_status__QRDelivery__supported(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, DeliveryMethod
        from altair.app.ticketing.payments.plugins import QR_DELIVERY_PLUGIN_ID

        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.payment_delivery_pair = PaymentDeliveryMethodPair(
            delivery_method=DeliveryMethod(delivery_plugin_id=QR_DELIVERY_PLUGIN_ID))
        self.assertTrue(target._is_supported_order(order))

    def test_supported_status__SEJDelivery__unsupported(self):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, DeliveryMethod
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID

        order = self._getOrder()
        history = self._getHistory()
        target = self._makeOne(order, history)

        order.payment_delivery_pair = PaymentDeliveryMethodPair(
            delivery_method=DeliveryMethod(delivery_plugin_id=SEJ_DELIVERY_PLUGIN_ID))
        self.assertFalse(target._is_supported_order(order))
