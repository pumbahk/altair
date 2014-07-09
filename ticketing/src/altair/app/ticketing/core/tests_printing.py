# -*- coding:utf-8 -*-
import unittest
from datetime import datetime

class Fixture(object):
    @staticmethod
    def pdmp(delivery_plugin_id):
        from altair.app.ticketing.core.models import PaymentDeliveryMethodPair, DeliveryMethod
        import altair.app.ticketing.orders.models
        return PaymentDeliveryMethodPair(
            system_fee=0,
            transaction_fee=0,
            delivery_fee_per_order=0,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            discount=0,
            special_fee=0, 
            delivery_method=DeliveryMethod(delivery_plugin_id=delivery_plugin_id, fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0)
            )


class OrderMarkIssuedOrPrintingTests(unittest.TestCase):
    def _getTarget(self):
        import altair.app.ticketing.core.models
        from altair.app.ticketing.orders.models import Order
        return Order

    def _makeOne(self, *args, **kwargs):
        from altair.app.ticketing.payments.plugins import RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        kwargs["payment_delivery_pair"] = Fixture.pdmp(RESERVE_NUMBER_DELIVERY_PLUGIN_ID)
        return self._getTarget()(*args, **kwargs)

    def _callFUT(self, target, *args, **kwargs):
        return target.mark_issued_or_printed(*args, **kwargs)

    def test_issued_or_printing_not_true__error(self):
        target = self._makeOne(
            issued_at=None, printed_at=None, 
        )
        with self.assertRaisesRegexp(ValueError, "issued or printed must be True"):
            self._callFUT(target, issued=False, printed=False)

    def test_printed_before_issued1(self):
        target = self._makeOne(issued_at=None, printed_at=None)
        with self.assertRaisesRegexp(Exception, "has not been issued"):
            self._callFUT(target, issued=False, printed=True)

    def test_it(self):
        from altair.app.ticketing.core.models import (
            ProductItem, 
            TicketBundle
        )
        from altair.app.ticketing.orders.models import (
            OrderedProductItem,
            OrderedProduct,
            OrderedProductItemToken,
            )
        target = self._makeOne(
            issued_at=None, printed_at=None, 
            items=[OrderedProduct(
                elements=[OrderedProductItem(
                    product_item=ProductItem(
                        ticket_bundle=TicketBundle()
                    ), 
                    tokens=[OrderedProductItemToken()]
                )])]
        )

        now = datetime(1000, 1, 1)
        self._callFUT(target, issued=True, printed=True, now=now)

        self.assertEqual(len(target.items), 1)
        self.assertEqual(len(target.items[0].elements), 1)
        self.assertEqual(len(target.items[0].elements[0].tokens), 1)


        self.assertEqual(target.printed_at, now)
        self.assertEqual(target.items[0].elements[0].printed_at, now)
        self.assertEqual(target.items[0].elements[0].issued_at, now)
        self.assertEqual(target.items[0].elements[0].tokens[0].printed_at, now)
        self.assertEqual(target.items[0].elements[0].tokens[0].issued_at, now)
