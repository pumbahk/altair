# -*- coding:utf-8 -*-

import unittest
from mock import patch
from pyramid import testing
from decimal import Decimal
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.cart.testing import CartTestMixin
from altair.app.ticketing.core.testing import CoreTestMixin
from datetime import datetime, timedelta

class FindApplicableTicketsTest(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from altair.app.ticketing.payments.plugins.sej import applicable_tickets_iter
        return applicable_tickets_iter(*args,  **kwargs)

    def test_it(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]
            tickets = [sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 1)

    def test_with_another_ticket(self):
        from altair.app.ticketing.payments.plugins import SEJ_DELIVERY_PLUGIN_ID as DELIVERY_PLUGIN_ID
        class bundle(object):
            class sej_ticket:
                class ticket_format:
                    sej_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=DELIVERY_PLUGIN_ID)                    
                    delivery_methods = [sej_delivery_method]

            class another_ticket:
                class ticket_format:
                    another_delivery_method = testing.DummyResource(fee=0, delivery_plugin_id=-100)                    
                    delivery_methods = [another_delivery_method]
                    
            tickets = [sej_ticket, another_ticket, sej_ticket, another_ticket, sej_ticket]

        result = list(self._callFUT(bundle))
        self.assertEquals(len(result), 3)

def get_items(cart_or_order):
    from altair.app.ticketing.core.models import Order
    from altair.app.ticketing.cart.models import Cart
    if isinstance(cart_or_order, Cart):
        return cart_or_order.products
    elif isinstance(cart_or_order, Order):
        return cart_or_order.ordered_products

def get_elements(cart_or_order):
    from altair.app.ticketing.core.models import OrderedProduct
    from altair.app.ticketing.cart.models import CartedProduct
    if isinstance(cart_or_order, CartedProduct):
        return cart_or_order.items
    elif isinstance(cart_or_order, OrderedProduct):
        return cart_or_order.ordered_product_items

class PluginTestBase(unittest.TestCase, CoreTestMixin, CartTestMixin):
    def setUp(self):
        from datetime import datetime
        self.session = _setup_db([
            'altair.app.ticketing.core.models',
            'altair.app.ticketing.sej.models',
            'altair.app.ticketing.cart.models'
            ])
        self.request = testing.DummyRequest()
        testing.setUp(request=self.request, settings={ 'sej.api_key': 'XXXXX', 'sej.inticket_api_url': 'http://example.com/' })
        CoreTestMixin.setUp(self)
        self._setup_fixture()
        self.performance.start_on = datetime(2012, 4, 1, 0, 0, 0)
        self.session.flush()


    @property
    def _payment_plugin_id(self):
        from . import SEJ_PAYMENT_PLUGIN_ID
        return SEJ_PAYMENT_PLUGIN_ID

    _delivery_plugin_id = 'N/A'

    @property
    def _payment_types(self):
        from altair.app.ticketing.sej.models import SejPaymentType
        return [
            SejPaymentType.CashOnDelivery,
            SejPaymentType.Prepayment,
            SejPaymentType.PrepaymentOnly,
            ]

    def _generate_ticket_formats(self):
        from altair.app.ticketing.core.models import TicketFormat
        yield self._create_ticket_format(delivery_methods=[
            delivery_method for delivery_method in self.delivery_methods.values()
            if delivery_method.delivery_plugin_id == self._delivery_plugin_id
            ])

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                if quantity == 0:
                    break
                quantity -= 1
                seat.status = SeatStatusEnum.InCart.v
                yield seat

    def _setup_fixture(self):
        from altair.app.ticketing.core.models import SalesSegmentGroup, SalesSegment
        from altair.app.ticketing.sej.models import SejPaymentType, SejTenant
        self.session.add(SejTenant(organization_id=1L))
        self.stock_types = self._create_stock_types(1)
        self.stock_types[0].quantity_only = False
        self.stocks = self._create_stocks(self.stock_types)
        self.seats = self._create_seats(self.stocks)
        self.products = self._create_products(self.stocks)
        for ticket in self.products[0].items[0].ticket_bundle.tickets:
            ticket.data = {u'drawing': u'''<?xml version="1.0" ?><svg xmlns="http://www.w3.org/2000/svg"><text>{{予約番号}}</text></svg>'''}
        self.sales_segment_group = SalesSegmentGroup(event=self.event)
        self.sales_segment = SalesSegment(performance=self.performance, sales_segment_group=self.sales_segment_group)
        self.pdmps = self._create_payment_delivery_method_pairs(self.sales_segment_group)
        self.applicable_pdmps = [
            pdmp for pdmp in self.pdmps
            if self._payment_plugin_id in (None, pdmp.payment_method.payment_plugin_id) or self._delivery_plugin_id in (None, pdmp.delivery_method.delivery_plugin_id)
            ]
        for pdmp in self.applicable_pdmps:
            pdmp.special_fee = Decimal(15)

    def _create_carts(self):
        from datetime import datetime
        carts = {}
        for payment_type in self._payment_types:
            cart = self._create_cart(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                pdmp=self.applicable_pdmps[0]
                )
            cart.performance = self.performance
            cart.created_at = datetime(2012, 1, 1, 0, 0, 0)
            carts[payment_type] = cart
        return carts

    def tearDown(self):
        testing.tearDown()
        self.session.remove()
        _teardown_db()


    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

class PaymentPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejPaymentPlugin
        return SejPaymentPlugin

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    }
                order = plugin.finish(self.request, cart)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertEqual(cart.order_no, order.order_no)

class DeliveryPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejDeliveryPlugin
        return SejDeliveryPlugin

    _payment_plugin_id = 'N/A'

    @property
    def _delivery_plugin_id(self):
        from . import SEJ_DELIVERY_PLUGIN_ID
        return SEJ_DELIVERY_PLUGIN_ID

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.sej.models import SejOrder, SejTicket

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    'X_barcode_no_01': '00000001',
                    }
                plugin.finish(self.request, cart)
                self.session.flush()
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                new_sej_order = self.session.query(SejOrder).filter_by(order_no=cart.order_no).one()
                new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
                self.assertTrue(len(new_sej_tickets), 1)
                self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

class PaymentDeliveryPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejPaymentDeliveryPlugin
        return SejPaymentDeliveryPlugin

    @property
    def _payment_plugin_id(self):
        from . import SEJ_PAYMENT_PLUGIN_ID
        return SEJ_PAYMENT_PLUGIN_ID

    @property
    def _delivery_plugin_id(self):
        from . import SEJ_DELIVERY_PLUGIN_ID
        return SEJ_DELIVERY_PLUGIN_ID

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum
        from altair.app.ticketing.sej.models import SejOrder, SejTicket

        carts = self._create_carts()
        plugin = self._makeOne()
        for payment_type, cart in carts.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_shop_order_id': cart.order_no,
                    'X_haraikomi_no': '00001001',
                    'X_hikikae_no': '00001002',
                    'X_url_info': 'http://example.com/',
                    'iraihyo_id_00': '10000000',
                    'X_goukei_kingaku': cart.total_amount,
                    'X_ticket_daikin': cart.total_amount - cart.system_fee - cart.delivery_fee - cart.transaction_fee - cart.special_fee,
                    'X_ticket_kounyu_daikin': cart.system_fee + cart.special_fee,
                    'X_hakken_daikin': cart.transaction_fee,
                    'X_barcode_no_01': '00000001',
                    }
                order = plugin.finish(self.request, cart)
                self.session.flush()
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                new_sej_order = self.session.query(SejOrder).filter_by(order_no=order.order_no).one()
                new_sej_tickets = self.session.query(SejTicket).filter_by(sej_order_id=new_sej_order.id).all()
                self.assertTrue(new_sej_tickets[0].barcode_number, '00000001')

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
