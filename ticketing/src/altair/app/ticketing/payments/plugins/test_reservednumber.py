import unittest
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from datetime import datetime

class ReservedNumberPaymentPluginTest(unittest.TestCase):
    def setUp(self):
        self.session = _setup_db([
            'altair.app.ticketing.users.models',
            'altair.app.ticketing.cart.models',
            'altair.app.ticketing.orders.models',
            'altair.app.ticketing.payments.plugins.models',
            ])

    def tearDown(self):
        _teardown_db()

    def _getTarget(self):
        from .reservednumber import ReservedNumberPaymentPlugin
        return ReservedNumberPaymentPlugin

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_finish(self):
        target = self._makeOne() 
        from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, Event, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, ShippingAddress, DateCalculationBase
        from altair.app.ticketing.cart.models import Cart
        from altair.app.ticketing.orders.models import Order
        from . import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        sales_segment_group = SalesSegmentGroup(
            event=Event(
                organization_id=0
                ),
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(
                    payment_method=PaymentMethod(payment_plugin_id=RESERVE_NUMBER_PAYMENT_PLUGIN_ID, fee=0),
                    delivery_method=DeliveryMethod(delivery_plugin_id=RESERVE_NUMBER_DELIVERY_PLUGIN_ID, fee_per_order=0, fee_per_principal_ticket=0, fee_per_subticket=0),
                    system_fee=0,
                    transaction_fee=0,
                    delivery_fee_per_order=0,
                    delivery_fee_per_principal_ticket=0,
                    delivery_fee_per_subticket=0,
                    discount=0,
                    payment_start_day_calculation_base=DateCalculationBase.Absolute.v,
                    payment_start_at=datetime(2015, 1, 2),
                    payment_due_day_calculation_base=DateCalculationBase.Absolute.v,
                    payment_due_at=datetime(2015, 1, 2),
                    issuing_start_day_calculation_base=DateCalculationBase.Absolute.v,
                    issuing_start_at=datetime(2015, 1, 2),
                    issuing_end_day_calculation_base=DateCalculationBase.Absolute.v,
                    issuing_end_at=datetime(2015, 1, 3),
                    ),
                ]
            )
        sales_segment = SalesSegment(
            sales_segment_group=sales_segment_group,
            payment_delivery_method_pairs=sales_segment_group.payment_delivery_method_pairs
            )
        cart = Cart(
            _order_no='000000000000',
            sales_segment=sales_segment,
            payment_delivery_pair=sales_segment.payment_delivery_method_pairs[0],
            shipping_address=ShippingAddress(),
            items=[],
            created_at=datetime(2015, 1, 1)
            )
        request = DummyRequest()
        order = target.finish(request, cart)
        self.assertEqual(order.order_no, cart.order_no)
        from .models import PaymentReservedNumber
        payment_reserved_number = self.session.query(PaymentReservedNumber).filter_by(order_no=order.order_no).first()
        self.assertIsNotNone(payment_reserved_number)

    def test_finish2(self):
        target = self._makeOne() 
        from altair.app.ticketing.core.models import SalesSegment, SalesSegmentGroup, PaymentDeliveryMethodPair, PaymentMethod, DeliveryMethod, ShippingAddress
        from altair.app.ticketing.orders.models import Order
        from . import RESERVE_NUMBER_PAYMENT_PLUGIN_ID, RESERVE_NUMBER_DELIVERY_PLUGIN_ID
        sales_segment_group = SalesSegmentGroup(
            payment_delivery_method_pairs=[
                PaymentDeliveryMethodPair(
                    payment_method=PaymentMethod(payment_plugin_id=RESERVE_NUMBER_PAYMENT_PLUGIN_ID),
                    delivery_method=DeliveryMethod(delivery_plugin_id=RESERVE_NUMBER_DELIVERY_PLUGIN_ID)
                    )
                ]
            )
        sales_segment = SalesSegment(
            sales_segment_group=sales_segment_group,
            payment_delivery_method_pairs=sales_segment_group.payment_delivery_method_pairs
            )
        order = Order(
            order_no='000000000000',
            sales_segment=sales_segment,
            payment_delivery_pair=sales_segment.payment_delivery_method_pairs[0],
            shipping_address=ShippingAddress(),
            total_amount=5000,
            created_at=datetime(2012, 10, 30, 12, 34, 56),
            issued_at=datetime(2012, 11, 1, 12, 34, 56),
            items=[]
            )
        request = DummyRequest()
        target.finish2(request, order)
        from .models import PaymentReservedNumber
        payment_reserved_number = self.session.query(PaymentReservedNumber).filter_by(order_no=order.order_no).first()
        self.assertIsNotNone(payment_reserved_number)

