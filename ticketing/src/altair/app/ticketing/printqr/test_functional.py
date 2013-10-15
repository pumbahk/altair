# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from datetime import datetime
import transaction
import sqlalchemy as sa
from .testing import (
    setUpSwappedDB, 
    tearDownSwappedDB, 
    DummyRequest
)

def setUpModule():
    setUpSwappedDB()

def tearDownModule():
    tearDownSwappedDB()

def setup_ordered_product_token_from_ordered_product_item(ordered_product_item):
    from altair.app.ticketing.core.models import OrderedProductItemToken
    for i, seat in ordered_product_item.iterate_serial_and_seat():
        token = OrderedProductItemToken(
            item = ordered_product_item, 
            serial = i, 
            seat = seat, 
            valid=True #valid=Falseの時は何時だろう？
        )

def setup_ticket_bundle(event, drawing):
    from altair.app.ticketing.core.models import TicketBundle
    from altair.app.ticketing.core.models import TicketFormat
    from altair.app.ticketing.core.models import Ticket
    ticket_format = TicketFormat(name=":TicketFormat:name")
    ticket_template = Ticket(name=":TicketTemplate:name", ticket_format=ticket_format, data={"drawing": drawing})
    ticket = Ticket(name="Ticket:name", ticket_format=ticket_format, event=event, data={"drawing": drawing})
    bundle = TicketBundle(name=":TicketBundle:name", event=event, tickets=[ticket])
    return bundle
    
def get_ordered_product_item__full_relation(quantity, quantity_only):
    """copied. from altair/app/ticketing/tickets/tests_builder_it.py"""
    from altair.app.ticketing.core.models import OrderedProductItemToken
    from altair.app.ticketing.core.models import OrderedProductItem
    from altair.app.ticketing.core.models import OrderedProduct
    from altair.app.ticketing.core.models import Stock
    from altair.app.ticketing.core.models import StockStatus
    from altair.app.ticketing.core.models import StockType
    from altair.app.ticketing.core.models import StockHolder
    from altair.app.ticketing.core.models import Performance
    from altair.app.ticketing.core.models import PerformanceSetting
    from altair.app.ticketing.core.models import Product
    from altair.app.ticketing.core.models import ProductItem
    from altair.app.ticketing.core.models import Order
    from altair.app.ticketing.core.models import ShippingAddress
    from altair.app.ticketing.core.models import SalesSegment
    from altair.app.ticketing.core.models import SalesSegmentGroup
    from altair.app.ticketing.core.models import Event
    from altair.app.ticketing.core.models import Organization
    from altair.app.ticketing.core.models import TicketBundle
    from altair.app.ticketing.core.models import Venue
    from altair.app.ticketing.core.models import Site
    from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
    from altair.app.ticketing.core.models import PaymentMethod
    from altair.app.ticketing.core.models import DeliveryMethod

    organization = Organization(name=":Organization:name",
                                      short_name=":Organization:short_name", 
                                      code=":Organization:code")

    sales_segment = SalesSegment(start_at=datetime(2000, 1, 1), 
                         end_at=datetime(2000, 1, 1, 23), 
                         upper_limit=8, 
                         seat_choice=True
                         )
    sales_segment.sales_segment_group = SalesSegmentGroup(
        name=":SalesSegmentGroup:name", 
        kind=":kind")

    shipping_address = ShippingAddress(
        email_1=":email_1",
        email_2=":email_2",
        nick_name=":nick_name",
        first_name=":first_name",
        last_name=":last_name",
        first_name_kana=":first_name_kana",
        last_name_kana=":last_name_kana",
        zip=":zip",
        country=":country",
        prefecture=":prefecture",
        city=":city",
        address_1=":address_1",
        address_2=":address_2",
        tel_1=":tel_1",
        tel_2=":tel_2",
        fax=":fax",
        )
    order = Order(shipping_address=shipping_address, 
                  total_amount=600, 
                  system_fee=100, 
                  transaction_fee=200, 
                  delivery_fee=300, 
                  multicheckout_approval_no=":multicheckout_approval_no", 
                  order_no=":order_no", 
                  paid_at=datetime(2000, 1, 1, 1, 10), 
                  delivered_at=None, 
                  canceled_at=None, 
                  created_at=datetime(2000, 1, 1, 1), 
                  issued_at=datetime(2000, 1, 1, 1, 13),                                        
                  )

    payment_delivery_method_pair = order.payment_delivery_pair = PaymentDeliveryMethodPair(system_fee=100, transaction_fee=200, delivery_fee=300, discount=0)
    payment_method = payment_delivery_method_pair.payment_method = PaymentMethod(name=":PaymentMethod:name", 
                          fee=300, 
                          fee_type=1, 
                          payment_plugin_id=2)
    delivery_method = payment_delivery_method_pair.delivery_method = DeliveryMethod(name=":DeliveryMethod:name", 
                          fee=300, 
                          fee_type=1, 
                          delivery_plugin_id=2)
    ordered_product = OrderedProduct(price=12000, 
                                     quantity=quantity)
    ordered_product.order = order
    ordered_product_item = OrderedProductItem(id=1, price=14000, quantity=quantity)
    ordered_product_item.ordered_product = ordered_product
    product_item = ordered_product_item.product_item = ProductItem(name=":ProductItem:name", 
                        price=12000, 
                        quantity=quantity, 
                        )
    product = product_item.product = Product(name=":Product:name", 
                                             price=10000)
    ordered_product.product = product
    product_item.product.sales_segment = sales_segment
    performance = order.performance = product_item.performance = Performance(name=":Performance:name",
                       code=":code", 
                       open_on=datetime(2000, 1, 1), 
                       start_on=datetime(2000, 1, 1, 10), 
                       end_on=datetime(2000, 1, 1, 23), 
                       abbreviated_title=":PerformanceSetting:abbreviated_title", 
                       subtitle=":PerformanceSetting:subtitle", 
                       note=":PerformanceSetting:note")
    performance.settings.append(PerformanceSetting())

    site = Site()
    venue = performance.venue = Venue(name=":Venue:name", 
                                      organization=organization, 
                                      sub_name=":sub_name", 
                                      site=site)

    event = performance.event = Event(title=":Event:title",
                  abbreviated_title=":abbreviated_title", 
                  organization=organization, 
                  code=":Event:code")
    ticket_bundle = event.ticket_bundle = TicketBundle()
    ticket_bundle.attributes = {"key": "value"}
    product_item.ticket_bundle = ticket_bundle
    stock = product_item.stock = Stock(quantity=10, performance=performance)
    stock.stock_type = StockType(name=":StockType:name", type=":type", display_order=50, quantity_only=quantity_only)
    stock.stock_holder = StockHolder(name=":StockHolder:name")
    stock.stock_status = StockStatus(quantity=10)
    return ordered_product_item

def make_view(view, context=None, request=None):
    from .resources import PrintQRResource
    request = request or DummyRequest()
    context = context or PrintQRResource(request)
    return view(context, request)
    
def qrsigned_from_token(token):
    from altair.app.ticketing.qr.utils import get_or_create_matched_history_from_token
    from altair.app.ticketing.qr import get_qrdata_builder
    from .views import _signed_string_from_history

    builder = get_qrdata_builder(DummyRequest())
    history = get_or_create_matched_history_from_token(order_no=None, token=token)
    return _signed_string_from_history(builder, history)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        cls.config.include('altair.app.ticketing.qr', route_prefix='qr')
        cls.config.include("altair.app.ticketing.printqr")

    @classmethod
    def tearDownClass(cls):
        testing.tearDown()

    def tearDown(self):
        transaction.abort()

    def test_it(self):
        def _getTarget():
            from .views import ticketdata_from_qrsigned_string
            return ticketdata_from_qrsigned_string

        from altair.app.ticketing.core.models import Event
        from altair.app.ticketing.models import DBSession
        item = get_ordered_product_item__full_relation(quantity=2, quantity_only=True)
        event = item.product_item.performance.event
        setup_ordered_product_token_from_ordered_product_item(item)
        bundle = setup_ticket_bundle(event, drawing="dummy")
        item.product_item.ticket_bundle = bundle
        DBSession.add(item)
        DBSession.add(bundle)
        DBSession.flush()

        ## qrcode
        token = item.tokens[0]
        token.id = 9999
        qrsigned = qrsigned_from_token(token)
        event_id = Event.query.first().id
        result = make_view(
            _getTarget(), 
            request=DummyRequest(params={"qrsigned": qrsigned}, 
                                 matchdict={"event_id": event_id})
        )
        """
        {'status': 'success', 'data': {'seat_id': None, 'performance_name': u':Performance:name (:Venue:name)', 'ordered_product_item_token_id': 9999, 'event_id': 1, 'order_id': 1, 'ordered_product_item_id': 1, 'seat_name': u'\u81ea\u7531\u5e2d', 'performance_date': u'2000\u5e741\u67081\u65e5(\u571f)10\u66420\u52060\u79d2', 'printed_at': None, 'canceled': None, 'refreshed_at': None, 'user': u':last_name_kana :first_name_kana', 'codeno': 1, 'orderno': ':order_no', 'product_name': ':Product:name', 'note': None, 'printed': None}}
        """
        self.assertEqual(str(result["data"]["ordered_product_item_token_id"]), str(token.id))
        
