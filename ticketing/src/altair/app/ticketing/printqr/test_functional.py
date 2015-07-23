# -*- coding:utf-8 -*-
import unittest
from pyramid import testing
from datetime import datetime
import transaction
import mock
from ..testing import SetUpTearDownManager 
from .testing import (
    setUpSwappedDB, 
    tearDownSwappedDB, 
    DummyRequest
)

def setUpModule():
    import altair.app.ticketing.core.models
    import altair.app.ticketing.cart.models
    import altair.app.ticketing.orders.models
    import altair.app.ticketing.users.models
    setUpSwappedDB()

def tearDownModule():
    tearDownSwappedDB()

def setup_ordered_product_token(ordered_product_item):
    from altair.app.ticketing.core import api as core_api
    from altair.app.ticketing.orders.models import OrderedProductItemToken
    for i, seat in core_api.iterate_serial_and_seat(ordered_product_item):
        token = OrderedProductItemToken(
            item = ordered_product_item, 
            serial = i, 
            seat = seat, 
            valid=True #valid=Falseの時は何時だろう？
        )

def setup_ticket_bundle(event, drawing):
    from altair.app.ticketing.core.models import TicketBundle
    from altair.app.ticketing.core.models import TicketFormat
    from altair.app.ticketing.core.models import PageFormat
    from altair.app.ticketing.core.models import Ticket
    page_format = PageFormat.query.first()
    if page_format is None:
        page_format = PageFormat(name=":PageFormat:name",
                                 printer_name=":PageFormat:printer_name",                             
                                 organization=event.organization,
                                 data={})
    ticket_format = TicketFormat.query.first()
    if ticket_format is None:
        ticket_format = TicketFormat(name=":TicketFormat:name",
                                     organization=event.organization,
                                     data={})
    ticket_template = Ticket(name=":TicketTemplate:name",
                             ticket_format=ticket_format,
                             organization=event.organization,
                             data={"drawing": drawing})
    ticket = Ticket(name="Ticket:name",
                    ticket_format=ticket_format,
                    event=event,
                    organization=event.organization,
                    data={"drawing": drawing})
    bundle = TicketBundle(name=":TicketBundle:name", event=event, tickets=[ticket])
    return bundle

ORGANIZATION_ID = 12345
AUTH_ID = 23456
    
def setup_operator(auth_id=AUTH_ID, organization_id=ORGANIZATION_ID):
    from altair.app.ticketing.operators.models import OperatorAuth
    from altair.app.ticketing.operators.models import Operator
    from altair.app.ticketing.core.models import Organization
    from altair.app.ticketing.core.models import OrganizationSetting
    operator = Operator.query.first()
    if operator is None:
        organization = Organization(name=":Organization:name",
                                    short_name=":Organization:short_name", 
                                    code=":Organization:code", 
                                    id=organization_id)
        OrganizationSetting(organization=organization, name="default")
        operator = Operator(organization_id=organization_id, organization=organization)
        OperatorAuth(operator=operator, login_id=auth_id)
    return operator

def setup_product_item(quantity, quantity_only, organization):
    from altair.app.ticketing.core.models import Stock
    from altair.app.ticketing.core.models import StockStatus
    from altair.app.ticketing.core.models import StockType
    from altair.app.ticketing.core.models import StockHolder
    from altair.app.ticketing.core.models import Performance
    from altair.app.ticketing.core.models import PerformanceSetting
    from altair.app.ticketing.core.models import Product
    from altair.app.ticketing.core.models import ProductItem
    from altair.app.ticketing.core.models import SalesSegment
    from altair.app.ticketing.core.models import SalesSegmentGroup
    from altair.app.ticketing.core.models import Event
    from altair.app.ticketing.core.models import Venue
    from altair.app.ticketing.core.models import Site
    from altair.app.ticketing.core.models import PaymentDeliveryMethodPair
    from altair.app.ticketing.core.models import PaymentMethod
    from altair.app.ticketing.core.models import DeliveryMethod

    sales_segment = SalesSegment(start_at=datetime(2000, 1, 1), 
                         end_at=datetime(2000, 1, 1, 23), 
                         max_quantity=8, 
                         seat_choice=True
                         )
    sales_segment.sales_segment_group = SalesSegmentGroup(
        name=":SalesSegmentGroup:name", 
        kind=":kind")

    payment_delivery_method_pair = PaymentDeliveryMethodPair(
        system_fee=100, 
        transaction_fee=200,
        delivery_fee_per_order=0,
        delivery_fee_per_principal_ticket=300, 
        delivery_fee_per_subticket=0,
        discount=0, 
        payment_method=PaymentMethod(
            name=":PaymentMethod:name", 
            fee=300, 
            fee_type=1, 
            payment_plugin_id=2), 
        delivery_method=DeliveryMethod(
            name=":DeliveryMethod:name", 
            fee_per_order=0,
            fee_per_principal_ticket=300, 
            fee_per_subticket=0,
            delivery_plugin_id=2)
    )

    sales_segment.payment_delivery_method_pairs.append(payment_delivery_method_pair)
    performance = Performance(
        name=":Performance:name",
        code=":code", 
        open_on=datetime(2000, 1, 1), 
        start_on=datetime(2000, 1, 1, 10), 
        end_on=datetime(2000, 1, 1, 23), 
        abbreviated_title=":PerformanceSetting:abbreviated_title", 
        subtitle=":PerformanceSetting:subtitle", 
        note=":PerformanceSetting:note", 
        event=Event(
            title=":Event:title",
            abbreviated_title=":abbreviated_title", 
            organization=organization, 
            code=":Event:code"), 
        venue=Venue(
            name=":Venue:name", 
            organization=organization, 
            sub_name=":sub_name", 
            site=Site()
        )
    )
    performance.setting = PerformanceSetting()

    product_item = ProductItem(
        name=":ProductItem:name", 
        price=12000, 
        quantity=quantity, 
        performance=performance, 
        product=Product(
            sales_segment=sales_segment, 
            name=":Product:name", 
            price=10000), 
        stock=Stock(
            quantity=10,
            performance=performance, 
            stock_type=StockType(
                name=":StockType:name",
                type=":type",
                display_order=50,
                quantity_only=quantity_only
            ), 
            stock_holder=StockHolder(name=":StockHolder:name"), 
            stock_status=StockStatus(quantity=10)
        )
    )
    return product_item

def setup_shipping_address(mail_address="my@test.mail.com"):
    from altair.app.ticketing.core.models import ShippingAddress
    return ShippingAddress(
            email_1=mail_address, #xxx:
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
            fax=":fax")


def setup_ordered_product_item(quantity, quantity_only, organization, order_no="Order:order_no", product_item=None):
    """copied. from altair/ticketing/src/altair/app/ticketing/printqr/test_functional.py"""
    from altair.app.ticketing.orders.models import (
        OrderedProductItem,
        OrderedProduct,
        Order,
        )

    product_item = product_item or setup_product_item(quantity, quantity_only, organization) #xxx:
    payment_delivery_method_pair = product_item.product.sales_segment.payment_delivery_method_pairs[0] #xxx:
    order = Order(
        shipping_address=setup_shipping_address(), #xxx:
        total_amount=600, 
        system_fee=100, 
        transaction_fee=200, 
        delivery_fee=300, 
        special_fee=400, 
        order_no=order_no, 
        paid_at=datetime(2000, 1, 1, 1, 10), 
        delivered_at=None, 
        canceled_at=None, 
        created_at=datetime(2000, 1, 1, 1), 
        issued_at=datetime(2000, 1, 1, 1, 13),
        issuing_start_at=datetime(1970, 1, 1),
        issuing_end_at=datetime(1970, 1, 1),
        payment_start_at=datetime(1970, 1, 1),
        payment_due_at=datetime(1970, 1, 1),
        organization_id=organization.id, 
        ordered_from=organization,  #xxx:
        payment_delivery_pair = payment_delivery_method_pair, 
        performance=product_item.performance, 
    )
    ordered_product = OrderedProduct(
        price=12000, 
        product=product_item.product, 
        order=order, 
        quantity=quantity
    )
    return OrderedProductItem(price=14000, quantity=quantity, product_item=product_item, ordered_product=ordered_product)


def do_view(view, context=None, request=None, attr=None):
    from .resources import PrintQRResource
    request = request or DummyRequest()
    context = context or PrintQRResource(request)

    with mock.patch("altair.app.ticketing.printqr.resources.authenticated_userid") as m:
        m.return_value = AUTH_ID
        result = view(context, request)
        if attr:
            return getattr(result, attr)()
        return result
    
def qrsigned_from_token(token):
    from altair.app.ticketing.qr.utils import get_or_create_matched_history_from_token
    from altair.app.ticketing.qr import get_qrdata_builder
    from altair.app.ticketing.qr.utils import make_data_for_qr

    builder = get_qrdata_builder(DummyRequest())
    assert token.ordered_product_item_id
    history = get_or_create_matched_history_from_token(order_no=None, token=token)
    history.ordered_product_item = token.item
    assert history.ordered_product_item_id
    assert history.ordered_product_item
    params, ticket = make_data_for_qr(history)
    return builder.sign(builder.make(params))


## todo: assertion strictly
class BaseTestMixin(object):
    @classmethod
    def setUpClass(cls):
        cls.config = testing.setUp()
        cls.config.include('pyramid_mako')
        cls.config.add_mako_renderer('.html')
        cls.config.include('altair.app.ticketing.qr', route_prefix='qr')
        cls.config.include("altair.app.ticketing.printqr")

    @classmethod
    def tearDownClass(cls):
        testing.tearDown()

    def tearDown(self):
        from .utils import reset_issuer
        reset_issuer()
        transaction.abort()

class QRTestsWithSeat(unittest.TestCase, BaseTestMixin):
    TOKEN_ID = 19999
    DRAWING_DATA = "drawing-data-for-svg"
    @classmethod
    def setUpClass(cls):
        BaseTestMixin.setUpClass()

        from altair.app.ticketing.models import DBSession
        from altair.app.ticketing.core.models import Seat
        operator = setup_operator()
        item = setup_ordered_product_item(quantity=1, quantity_only=False,
                                           organization=operator.organization, order_no="Demo:OrderNO:02")
        event = item.product_item.performance.event
        seat = Seat(l0_id=":l0_id", 
                    seat_no=":seat_no", 
                    name=":Seat:name", 
                    stock = item.product_item.stock, 
                    venue = item.product_item.performance.venue)
        item.seats.append(seat)
        setup_ordered_product_token(item)
        bundle = setup_ticket_bundle(event, drawing=cls.DRAWING_DATA)
        item.product_item.ticket_bundle = bundle
        DBSession.add(item)
        DBSession.add(bundle)
        DBSession.add(operator)

        seat = Seat(l0_id=":l0_id", 
                    seat_no=":seat_no", 
                    name=":Seat:name", 
                    stock = item.product_item.stock, 
                    venue = item.product_item.performance.venue)
        item.seats.append(seat)

        token = item.tokens[0]
        token.id = cls.TOKEN_ID

        cls.item = property(lambda self: DBSession.merge(item))
        cls.token = property(lambda self: DBSession.merge(token))
        cls.event = property(lambda self: DBSession.merge(self.item.product_item.performance.event))
        cls.order = property(lambda self: DBSession.merge(self.item.ordered_product.order))
        cls.budnle = property(lambda self: DBSession.merge(bundle))
        cls.ticket = property(lambda self: DBSession.merge(bundle).tickets[0])
        transaction.commit()

    def test_ticket_data(self):
        def _getTarget():
            from .views import AppletAPIView
            return AppletAPIView
        result = do_view(
            _getTarget(), 
            request=DummyRequest(json_body={"ordered_product_item_token_id": self.token.id}, 
                                 matchdict={"event_id": self.event.id}), 
            attr="ticket_data")
        self.assertEquals(len(result["data"]), 1)
        self.assertEquals(result["data"][0][u'ordered_product_item_token_id'], self.token.id)

        self.assertEquals(result["data"][0]["data"][u"席番"], u":Seat:name") #xxx!

        self.assertEquals(result["data"][0]["data"][u"イベント名"], ":Event:title")
        self.assertEquals(result["data"][0]["data"][u"対戦名"], ":Performance:name")
        self.assertEquals(result["data"][0]["data"][u"開始時刻"], u"10時 00分")
        self.assertEquals(result["data"][0]["data"][u"会場名"], ":Venue:name")
        self.assertEquals(result["data"][0]["data"][u"チケット価格"], u"14,000円")
        self.assertEquals(result["data"][0]["data"][u"席種名"], ":StockType:name")
        self.assertEquals(result["data"][0]["data"][u"商品名"], ":ProductItem:name")
        self.assertEquals(result["data"][0]["data"][u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")

    def test_ticket_data_order(self):
        def _getTarget():
            from .views import AppletAPIView
            return AppletAPIView
        result = do_view(
            _getTarget(), 
            request=DummyRequest(json_body={"order_no": self.order.order_no}, 
                                 matchdict={"event_id": self.event.id}), 
            attr="ticket_data_order")
        self.assertEquals(len(result["data"]), 1)
        self.assertEquals(result["data"][0][u'ordered_product_item_token_id'], self.token.id)

        self.assertEquals(result["data"][0]["data"][u"イベント名"], ":Event:title")
        self.assertEquals(result["data"][0]["data"][u"対戦名"], ":Performance:name")
        self.assertEquals(result["data"][0]["data"][u"開始時刻"], u"10時 00分")
        self.assertEquals(result["data"][0]["data"][u"会場名"], ":Venue:name")
        self.assertEquals(result["data"][0]["data"][u"チケット価格"], u"14,000円")
        self.assertEquals(result["data"][0]["data"][u"席種名"], ":StockType:name")
        self.assertEquals(result["data"][0]["data"][u"商品名"], ":ProductItem:name")
        self.assertEquals(result["data"][0]["data"][u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")


class QRTestsWithoutSeat(unittest.TestCase, BaseTestMixin):
    TOKEN_ID = 9999
    DRAWING_DATA = "drawing-data-for-svg"
    @classmethod
    def setUpClass(cls):
        BaseTestMixin.setUpClass()

        from altair.app.ticketing.models import DBSession
        operator = setup_operator()
        item = setup_ordered_product_item(quantity=2, quantity_only=True,
                                           organization=operator.organization, order_no="Demo:OrderNO:01")
        event = item.product_item.performance.event
        setup_ordered_product_token(item)
        bundle = setup_ticket_bundle(event, drawing=cls.DRAWING_DATA)
        item.product_item.ticket_bundle = bundle
        DBSession.add(item)
        DBSession.add(bundle)
        DBSession.add(operator)

        token = item.tokens[0]
        token.id = cls.TOKEN_ID

        cls.item = property(lambda self: DBSession.merge(item))
        cls.token = property(lambda self: DBSession.merge(token))
        cls.event = property(lambda self: DBSession.merge(self.item.product_item.performance.event))
        cls.order = property(lambda self: DBSession.merge(self.item.ordered_product.order))
        cls.budnle = property(lambda self: DBSession.merge(bundle))
        cls.ticket = property(lambda self: DBSession.merge(bundle).tickets[0])
        transaction.commit()

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_ticketdata_from_qrsigned_string__success(self):
        def _getTarget():
            from .views import ticketdata_from_qrsigned_string
            return ticketdata_from_qrsigned_string

        ## qrcode
        qrsigned = qrsigned_from_token(self.token)
        event_id = self.event.id
        result = do_view(
            _getTarget(), 
            request=DummyRequest(params={"qrsigned": qrsigned}, 
                                 matchdict={"event_id": event_id})
        )
        self.assertEqual(str(result["data"]["ordered_product_item_token_id"]), 
                         str(self.token.id))

    def test_ticket_data(self):
        def _getTarget():
            from .views import AppletAPIView
            return AppletAPIView
        result = do_view(
            _getTarget(), 
            request=DummyRequest(json_body={"ordered_product_item_token_id": self.token.id}, 
                                 matchdict={"event_id": self.event.id}), 
            attr="ticket_data")
        self.assertEquals(len(result["data"]), 1)
        self.assertEquals(result["data"][0][u'ordered_product_item_token_id'], self.token.id)

        self.assertEquals(result["data"][0]["data"][u"イベント名"], ":Event:title")
        self.assertEquals(result["data"][0]["data"][u"対戦名"], ":Performance:name")
        self.assertEquals(result["data"][0]["data"][u"開始時刻"], u"10時 00分")
        self.assertEquals(result["data"][0]["data"][u"会場名"], ":Venue:name")
        self.assertEquals(result["data"][0]["data"][u"チケット価格"], u"14,000円")
        self.assertEquals(result["data"][0]["data"][u"席種名"], ":StockType:name")
        self.assertEquals(result["data"][0]["data"][u"商品名"], ":ProductItem:name")
        self.assertEquals(result["data"][0]["data"][u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")

        self.assertEquals(result["data"][0]["data"][u"発券番号"], 1)

    def test_ticket_data_order(self):
        def _getTarget():
            from .views import AppletAPIView
            return AppletAPIView
        result = do_view(
            _getTarget(), 
            request=DummyRequest(json_body={"order_no": self.order.order_no}, 
                                 matchdict={"event_id": self.event.id}), 
            attr="ticket_data_order")
        self.assertEquals(len(result["data"]), 2)
        self.assertEquals(result["data"][0][u'ordered_product_item_token_id'], self.token.id)

        self.assertEquals(result["data"][0]["data"][u"イベント名"], ":Event:title")
        self.assertEquals(result["data"][0]["data"][u"対戦名"], ":Performance:name")
        self.assertEquals(result["data"][0]["data"][u"開始時刻"], u"10時 00分")
        self.assertEquals(result["data"][0]["data"][u"会場名"], ":Venue:name")
        self.assertEquals(result["data"][0]["data"][u"チケット価格"], u"14,000円")
        self.assertEquals(result["data"][0]["data"][u"席種名"], ":StockType:name")
        self.assertEquals(result["data"][0]["data"][u"商品名"], ":ProductItem:name")
        self.assertEquals(result["data"][0]["data"][u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")

        self.assertEquals(result["data"][1]["data"][u"イベント名"], ":Event:title")
        self.assertEquals(result["data"][1]["data"][u"対戦名"], ":Performance:name")
        self.assertEquals(result["data"][1]["data"][u"開始時刻"], u"10時 00分")
        self.assertEquals(result["data"][1]["data"][u"会場名"], ":Venue:name")
        self.assertEquals(result["data"][1]["data"][u"チケット価格"], u"14,000円")
        self.assertEquals(result["data"][1]["data"][u"席種名"], ":StockType:name")
        self.assertEquals(result["data"][1]["data"][u"商品名"], ":ProductItem:name")
        self.assertEquals(result["data"][1]["data"][u"受付日時"], u"2000年 01月 01日 (土) 01時 00分")

        self.assertEquals(result["data"][0]["data"][u"発券番号"], 1)
        self.assertEquals(result["data"][1]["data"][u"発券番号"], 2)

    @mock.patch("altair.app.ticketing.printqr.views.datetime")
    def test_refresh_printed_status(self, m):
        m.now.return_value = datetime(2000, 1, 1)

        def _getTarget():
            from .views import refresh_printed_status
            return refresh_printed_status
        
        def setup():
            self.token.printed_at = datetime(2000, 1, 1)
            
        def teardown():
            self.token.printed_at = None
            self.token.refreshed_at = None
            
        with SetUpTearDownManager(setup, teardown):
            result = do_view(
                _getTarget(), 
                request=DummyRequest(
                    json_body={
                        "ordered_product_item_token_id": str(self.token.id), 
                        "order_no": str(self.order.order_no)
                    }                   
                )
            )
            self.assertEquals(result["status"], "success")
            self.assertEqual(self.token.refreshed_at, datetime(2000, 1, 1))

    @mock.patch("altair.app.ticketing.printqr.views.datetime")
    def test_ticket_update_token_status(self, m):
        m.now.return_value = datetime(2000, 1, 1)

        from altair.app.ticketing.core.utils import PrintedAtBubblingSetter
        from altair.app.ticketing.core.models import TicketPrintHistory
        def teardown():
            ## todo: not use bubbling.
            setter = PrintedAtBubblingSetter(None)
            setter.printed_token(self.token)
            setter.start_bubbling()
            self.assertEqual(self.token.printed_at, None)
            
        def _getTarget():
            from .views import ticket_after_printed_edit_status
            return ticket_after_printed_edit_status
           
        with SetUpTearDownManager(teardown=teardown):
            prev = TicketPrintHistory.query.count()
            result = do_view(
                _getTarget(), 
                request=DummyRequest(json_body={"ordered_product_item_token_id": str(self.token.id), 
                                                "order_no": self.order.order_no, 
                                                "ticket_id": self.ticket.id}, 
                                     matchdict={"event_id": self.event.id}), 
            )
            self.assertEquals(TicketPrintHistory.query.count(), prev+1)
            self.assertEquals(result["data"], {'printed': '2000-01-01 00:00:00'})
            
    @mock.patch("altair.app.ticketing.printqr.views.datetime")
    def test_ticket_update_token_status_order(self, m):
        m.now.return_value = datetime(2000, 1, 1)

        def _getTarget():
            from .views import ticket_after_printed_edit_status_order
            return ticket_after_printed_edit_status_order
            
        from altair.app.ticketing.core.models import TicketPrintHistory
        prev = TicketPrintHistory.query.count()
        result = do_view(
            _getTarget(), 
            request=DummyRequest(json_body={"ordered_product_item_token_id": str(self.token.id), 
                                            "order_no": self.order.order_no, 
                                            "order_id": self.order.id, 
                                            "consumed_tokens": [t.id for t in self.item.tokens]
                                        }, 
                                 matchdict={"event_id": self.event.id}), 
        )
        self.assertEquals(TicketPrintHistory.query.count(), prev+2)
        self.assertEquals(result["data"], {'printed': '2000-01-01 00:00:00'})

    ## from applet
    def test_fetch_ticket_format_candidates(self):
        def _getTarget():
            from .views import AppletAPIView
            return AppletAPIView

        result = do_view(
            _getTarget(), 
            request=DummyRequest(
                matchdict={"event_id": str(self.event.id), "id": ""}
            ), 
            attr="ticket"
        )
        self.assertEquals(result["data"]["page_formats"], 
                          [{u'printer_name': u':PageFormat:printer_name', u'id': 1, u'name': u':PageFormat:name'}])

        self.assertEquals(result["data"]["ticket_formats"],
                          [{u'id': 1, u'name': u':TicketFormat:name'}])

        self.assertEquals(len(result["data"]["ticket_templates"]),1)
        self.assertEquals(result["data"]["ticket_templates"][0][u'ticket_format_id'], 1)
        self.assertEquals(result["data"]["ticket_templates"][0][u'drawing'], u'drawing-data-for-svg')
        self.assertEquals(result["data"]["ticket_templates"][0][u'name'], u'Ticket:name')
