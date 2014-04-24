import unittest
from pyramid import testing
from decimal import Decimal

class GetRefundPerOrderFeeTest(unittest.TestCase):
    def _getTarget(self):
        from .api import get_refund_per_order_fee
        return get_refund_per_order_fee

    def _callFUT(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _build_dummy_order(self):
        return testing.DummyModel(
            payment_delivery_pair=testing.DummyModel(
                transaction_fee_per_order=Decimal(11),
                delivery_fee_per_order=Decimal(5)
                ),
            system_fee=Decimal(13),
            transaction_fee=Decimal(17),
            delivery_fee=Decimal(19),
            special_fee=Decimal(23),
            items=[
                testing.DummyModel(
                    price=Decimal(13),
                    quantity=1,
                    elements=[
                        testing.DummyModel(
                            price=Decimal(7),
                            quantity=1,
                            product_item=testing.DummyModel(
                                price=Decimal(5),
                                ticket_bundle_id=1
                                )
                            ),
                        testing.DummyModel(
                            price=Decimal(3),
                            quantity=2,
                            product_item=testing.DummyModel(
                                price=Decimal(13),
                                ticket_bundle_id=None
                                )
                            ),
                        ]
                    )
                ]
            )

    def test_get_refund_per_order_fee_1(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(0))

    def test_get_refund_per_order_fee_2(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(13))

    def test_get_refund_per_order_fee_3(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=True,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(11))

    def test_get_refund_per_order_fee_4(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=True,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(5))

    def test_get_refund_per_order_fee_5(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=True,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(23))

    def test_get_refund_per_order_fee_6(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=True,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(24))

    def test_get_refund_per_order_fee_7(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=True,
            include_delivery_fee=True,
            include_special_fee=False,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(16))

    def test_get_refund_per_order_fee_8(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=True,
            include_special_fee=True,
            include_item=False
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(28))

    def test_get_refund_per_order_fee_9(self):
        refund = testing.DummyModel(
            include_system_fee=False,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(6))

    def test_get_refund_per_order_fee_10(self):
        refund = testing.DummyModel(
            include_system_fee=True,
            include_transaction_fee=False,
            include_delivery_fee=False,
            include_special_fee=False,
            include_item=True
            )
        order = self._build_dummy_order()
        result = self._callFUT(refund, order)
        self.assertEqual(result, Decimal(19))

