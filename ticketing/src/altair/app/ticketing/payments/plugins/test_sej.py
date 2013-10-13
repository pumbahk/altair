# -*- coding:utf-8 -*-

import unittest
from mock import patch
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.cart.testing import CartTestMixin

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

    def _create_order_pairs(self):
        from datetime import datetime
        order_pairs = {}
        for payment_type in self._payment_types:
            order = self._create_order(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                pdmp=self.applicable_pdmps[0]
                )
            order.created_at = datetime(2012, 1, 1, 0, 0, 0)
            sej_order = self._create_sej_order(order, payment_type)
            self.session.add(order)
            self.session.add(sej_order)
            order_pairs[payment_type] = (order, sej_order)
        return order_pairs

    def _create_cart_pairs(self):
        from datetime import datetime
        cart_pairs = {}
        for payment_type in self._payment_types:
            cart = self._create_cart(
                zip(self.products, [1]),
                sales_segment=self.sales_segment,
                pdmp=self.applicable_pdmps[0]
                )
            cart.performance = self.performance
            cart.created_at = datetime(2012, 1, 1, 0, 0, 0)
            sej_order = self._create_sej_order(cart, payment_type)
            self.session.add(cart)
            self.session.add(sej_order)
            cart_pairs[payment_type] = (cart, sej_order)
        return cart_pairs

    def tearDown(self):
        testing.tearDown()
        self.session.remove()
        _teardown_db()

    def _create_sej_order(self, order, payment_type):
        from altair.app.ticketing.sej.models import SejOrder, SejTicket, SejTicketType, SejPaymentType
        from datetime import datetime, timedelta
        tickets = [
            SejTicket(
                ticket_idx=(i + 1),
                ticket_type=('%d' % SejTicketType.TicketWithBarcode.v),
                barcode_number='0000%04d' % (i + 1),
                event_name=order.sales_segment.performance.event.title,
                performance_name=order.sales_segment.performance.name,
                performance_datetime=datetime(2012,8,30,19,00),
                ticket_template_id='TTTS0001',
                ticket_data_xml=u'<?xml version="1.0" encoding="Shift_JIS" ?><TICKET></TICKET>',
                product_item_id=12345
                )
            for ordered_product in order.items
            for i, ordered_product_item in enumerate(ordered_product.elements)
            ]

        return SejOrder(
            payment_type='%d' % int(payment_type),
            order_no=order.order_no,
            billing_number=u'00000001',
            total_ticket_count=len(tickets),
            ticket_count=len(tickets),
            total_price=order.total_amount,
            ticket_price=(order.total_amount - order.system_fee - order.transaction_fee - order.delivery_fee),
            commission_fee=order.system_fee,
            ticketing_fee=order.delivery_fee,
            branch_no=1,
            exchange_sheet_url=u'https://www.r1test.com/order/hi.do',
            exchange_sheet_number=u'11111111',
            exchange_number=u'22222222',
            order_at=order.created_at,
            ticketing_due_at=(order.created_at + timedelta(days=10)),
            regrant_number_due_at=(order.created_at + timedelta(days=5)),
            tickets=tickets
            )

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

class PaymentPluginTest(PluginTestBase):
    def _getTarget(self):
        from .sej import SejPaymentPlugin
        return SejPaymentPlugin

    def test_finish(self):
        from altair.app.ticketing.core.models import SeatStatusEnum

        cart_pairs = self._create_cart_pairs()
        plugin = self._makeOne()
        for payment_type, (cart, sej_order)  in cart_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    }
                order = plugin.finish(self.request, cart)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertEqual(cart.order_no, order.order_no)

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)

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

        cart_pairs = self._create_cart_pairs()
        plugin = self._makeOne()
        for payment_type, (cart, sej_order)  in cart_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000001',
                    }
                order = plugin.finish(self.request, cart)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000002',
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

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

        cart_pairs = self._create_cart_pairs()
        plugin = self._makeOne()
        for payment_type, (cart, sej_order)  in cart_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000001',
                    }
                order = plugin.finish(self.request, cart)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000001')

    def test_refresh(self):
        order_pairs = self._create_order_pairs()
        plugin = self._makeOne()
        for payment_type, (order, sej_order)  in order_pairs.items():
            with patch('altair.app.ticketing.sej.payment.SejPayment') as SejPayment:
                SejPayment.return_value.response = {
                    'X_haraikomi_no': sej_order.billing_number,
                    'X_hikikae_no': sej_order.exchange_number,
                    'X_url_info': sej_order.exchange_sheet_url,
                    'iraihyo_id_00': sej_order.exchange_sheet_number,
                    'X_goukei_kingaku': sej_order.total_price,
                    'X_ticket_daikin': sej_order.ticket_price,
                    'X_ticket_kounyu_daikin': sej_order.commission_fee,
                    'X_hakken_daikin': sej_order.ticketing_fee,
                    'X_barcode_no_01': '00000002',
                    }
                plugin.refresh(self.request, order)
                self.assertTrue(SejPayment.called)
                self.assertTrue(SejPayment.return_value.request.called)
                self.assertTrue(sej_order.tickets[0].barcode_number, '00000002')

if __name__ == "__main__":
    # setUpModule()
    unittest.main()
    
