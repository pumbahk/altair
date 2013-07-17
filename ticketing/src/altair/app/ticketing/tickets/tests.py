# encoding: utf-8

from unittest import TestCase
from datetime import datetime
from lxml import etree

class TicketsUtilsTest(TestCase):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.organization = None
        self.event = None
        self.performance = None
        self.stock_type = None
        self.stock_holder = None
        self.stock = None
        self.stock_status = None
        self.site = None
        self.venue = None
        self.seat = None
        self.sales_segment = None
        self.payment_method_multicheckout = None
        self.payment_method_cvs = None
        self.delivery_method_shipping = None
        self.delivery_method_qr = None
        self.delivery_method_cvs = None
        self.ticket_kp3000c = None
        self.ticket_sej = None
        self.product = None
        self.shipping_address = None
        self.order = None

    def build_fixture(self):
        from altair.app.ticketing.core.models import (
            Organization,
            Event,
            Performance,
            StockType,
            StockTypeEnum,
            StockHolder,
            Stock,
            StockStatus,
            Venue,
            Seat,
            SeatStatus,
            SeatStatusEnum,
            SalesSegment,
            SalesSegmentGroup,
            SalesSegmentKindEnum,
            PaymentDeliveryMethodPair,
            PaymentMethod,
            DeliveryMethod,
            PaymentMethodPlugin,
            DeliveryMethodPlugin,
            Product,
            ProductItem,
            Order,
            OrderedProduct,
            OrderedProductItem,
            Ticket,
            TicketFormat,
            TicketBundle,
            TicketBundleAttribute,
            ShippingAddress,
            OrderedProductItemToken,
            )
        from altair.app.ticketing.cart.models import (
            Cart,
            CartedProduct,
            CartedProductItem,
            )
        from altair.app.ticketing.payments.plugins import (
            MULTICHECKOUT_PAYMENT_PLUGIN_ID,
            SEJ_PAYMENT_PLUGIN_ID,
            SHIPPING_DELIVERY_PLUGIN_ID,
            SEJ_DELIVERY_PLUGIN_ID,
            QR_DELIVERY_PLUGIN_ID,
            )
        from altair.app.ticketing.users.models import SexEnum
        def _():
            organization = Organization(
                name=u'組織名',
                code=u'RT'
                )
            payment_method_multicheckout = PaymentMethod(
                organization=organization,
                _payment_plugin=PaymentMethodPlugin(
                    id=MULTICHECKOUT_PAYMENT_PLUGIN_ID,
                    name=u'クレジットカード決済'
                    )
                )
            payment_method_cvs = PaymentMethod(
                organization=organization,
                _payment_plugin=PaymentMethodPlugin(
                    id=SEJ_PAYMENT_PLUGIN_ID,
                    name=u'コンビニ決済'
                    )
                )
            delivery_method_shipping = DeliveryMethod(
                organization=organization,
                _delivery_plugin=DeliveryMethodPlugin(
                    id=SHIPPING_DELIVERY_PLUGIN_ID,
                    name=u'郵送'
                    )
                )
            delivery_method_qr = DeliveryMethod(
                organization=organization,
                _delivery_plugin=DeliveryMethodPlugin(
                    id=QR_DELIVERY_PLUGIN_ID,
                    name=u'QRコード'
                    )
                )
            delivery_method_cvs = DeliveryMethod(
                organization=organization,
                _delivery_plugin=DeliveryMethodPlugin(
                    id=SEJ_DELIVERY_PLUGIN_ID,
                    name=u'コンビニ受取'
                    )
                )
            sales_segment_group = SalesSegmentGroup(
                name=u'一般販売',
                kind=SalesSegmentKindEnum.normal.v
                )
            sales_segment = SalesSegment(
                sales_segment_group=sales_segment_group,
                start_at=datetime(2012, 12, 1, 10, 1, 2),
                end_at=datetime(2012, 12, 30, 0, 0, 0),
                upper_limit=10,
                seat_choice=True,
                public=True,
                payment_delivery_method_pairs=[
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_multicheckout,
                        delivery_method=delivery_method_shipping
                        ),
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_multicheckout,
                        delivery_method=delivery_method_qr
                        ),
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_multicheckout,
                        delivery_method=delivery_method_cvs
                        ),
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_cvs,
                        delivery_method=delivery_method_shipping
                        ),
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_cvs,
                        delivery_method=delivery_method_qr
                        ),
                    PaymentDeliveryMethodPair(
                        payment_method=payment_method_cvs,
                        delivery_method=delivery_method_cvs
                        ),
                    ]
                )
            event = Event(
                code=u'RTTST',
                title=u'イベント名',
                abbreviated_title=u'イベント名略称',
                organization=organization,
                sales_segment_groups=[sales_segment_group]
                )
            performance = Performance(
                event=event,
                name=u'パフォーマンス名',
                code=u'RTTST0000000',
                open_on=datetime(2012, 12, 31, 10, 1, 2),
                start_on=datetime(2012, 12, 31, 11, 3, 4),
                end_on=None,
                sales_segments=[sales_segment]
                )
            stock_type = StockType(
                name=u'S席',
                type=StockTypeEnum.Seat.v,
                display_order=0,
                quantity_only=0,
                event=event
                )
            stock_holder = StockHolder(
                name=u'stock_holder'
                )
            stock = Stock(
                performance=performance,
                stock_type=stock_type,
                stock_holder=stock_holder,
                quantity=100,
                stock_status=StockStatus(
                    quantity=98
                    )
                )
            venue = Venue(
                performance=performance,
                name=u'会場名',
                sub_name=u'サブ会場名'
                )
            seat = Seat(
                l0_id=u'l0_id',
                name=u'seat_name',
                seat_no=u'seat_no',
                stock=stock,
                status_=SeatStatus(status=SeatStatusEnum.Ordered.v),
                venue=venue,
                attributes={
                    u'a': u'b',
                    u'c': u'd'
                    }
                )
            ticket_kp3000c = Ticket(
                organization=organization,
                event=event,
                ticket_format=TicketFormat(
                    name=u'KP3000C',
                    organization=organization,
                    delivery_methods=[
                        delivery_method_shipping,
                        delivery_method_qr
                        ]
                    )
                )
            ticket_sej = Ticket(
                organization=organization,
                event=event,
                ticket_format=TicketFormat(
                    name=u'セブン-イレブン',
                    organization=organization,
                    delivery_methods=[delivery_method_cvs]
                    )
                )
            ticket_bundle = TicketBundle(
                tickets=[
                    ticket_kp3000c,
                    ticket_sej
                    ],
                attributes={
                    u'属性1': u'属性1の値',
                    u'属性2': u'属性2の値',
                    }
                )
            product = Product(
                event=seat.venue.performance.event,
                sales_segment=sales_segment,
                name=u'S席大人',
                price=5000,
                items=[
                    ProductItem(
                        name=u'S席大人',
                        stock=seat.stock,
                        quantity=1,
                        price=5000,
                        performance=seat.venue.performance,
                        ticket_bundle=ticket_bundle
                        )
                    ]
                )
            shipping_address = ShippingAddress(
                email_1=u'email@example.com',
                nick_name=u'nickname',
                first_name=u'姓',
                last_name=u'名',
                first_name_kana=u'セイ',
                last_name_kana=u'メイ',
                sex=SexEnum.Male.v,
                zip=u'1410022',
                country=u'Japan',
                prefecture='東京都',
                city=u'品川区',
                address_1=u'東五反田5-21-15',
                address_2=u'メタリオンOSビル7F',
                tel_1=u'09000000000',
                tel_2=u'09000000001'
                )
            order = Order(
                order_no='000000000000',
                payment_delivery_pair=sales_segment.payment_delivery_method_pairs[0],
                shipping_address=shipping_address,
                total_amount=5000,
                created_at=datetime(2012, 10, 30, 12, 34, 56),
                issued_at=datetime(2012, 11, 1, 12, 34, 56),
                items=[]
                )
            ordered_product = OrderedProduct(
                order=order,
                price=5000,
                product=product,
                ordered_product_items=[
                    OrderedProductItem(
                        price=5000,
                        product_item=product.items[0],
                        tokens=[
                            OrderedProductItemToken(
                                seat=seat,
                                serial=0,
                                valid=True
                                )
                            ],
                        seats=[seat]
                        )
                    ]
                )
            order.items.append(ordered_product)
            cart = Cart(
                _order_no='000000000000',
                payment_delivery_pair=sales_segment.payment_delivery_method_pairs[0],
                shipping_address=shipping_address,
                created_at=datetime(2012, 10, 30, 12, 34, 56),
                system_fee=0.,
                products=[]
                )
            carted_product = CartedProduct(
                cart=cart,
                product=product,
                quantity=1,
                items=[
                    CartedProductItem(
                        product_item=product.items[0],
                        quantity=1,
                        seats=[seat]
                        )
                    ]
                )
            cart.products.append(carted_product)
            for k, v in locals().iteritems():
                setattr(self, k, v)
        _()

    def setUp(self):
        self.build_fixture()

    def test_build_dict_from_seat(self):
        from altair.app.ticketing.tickets.utils import build_dict_from_seat

        seat = self.seat
        out = build_dict_from_seat(seat, None)
        expected = {
            u"organization": {
                u"name": u"組織名",
                u"code": u"RT"
                },
            u"event": {
                u"code": u"RTTST",
                u"title": u"イベント名",
                u"abbreviated_title": u"イベント名略称"
                },
            u"performance": {
                u"name": u"パフォーマンス名",
                u"code": u"RTTST0000000",
                u"open_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 10, u"minute": 1, u"second": 2, 
                    u"weekday": 0, 
                    },
                u"start_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 11, u"minute": 3, u"second": 4, 
                    u"weekday": 0, 
                    },
                u"end_on": None, 
                },
            u"venue": {
                u"name": u"会場名",
                u"sub_name": u"サブ会場名"
                },
            u"stock": {
                u"quantity": 100
                },
            u"stockStatus": {
                u"quantity": 98,
                },
            u"stockHolder": {
                u"name": u"stock_holder"
                },
            u"stockType": {
                u"name": u"S席",
                u"type": 0,
                u"display_order": 0,
                u"quantity_only": 0
                },
            u"seat": {
                u"l0_id": u"l0_id",
                u"name": u"seat_name",
                u"seat_no": u"seat_no"
                },
            u"イベント名": u"イベント名",
            u"パフォーマンス名": u"パフォーマンス名",
            u"対戦名": u"パフォーマンス名",
            u"会場名": u"会場名",
            u"公演コード": u"RTTST0000000",
            u"開催日": u"2012年 12月 31日 (月)",
            u"開場時刻": u"10時 01分",
            u"開場時刻s": u"10:01",
            u"開始時刻": u"11時 03分",
            u"開始時刻s": u"11:03",
            u"終了時刻": u"",
            u"席種名": u"S席",
            u"席番": u"seat_name",
            u"発券番号": None 
            }
        for k in expected:
            self.assertEqual(expected[k], out[k], (u"%s: expected %s, got %s" % (k, expected[k], out[k])).encode('utf-8'))

    def test_build_dicts_from_ordered_product_item(self):
        from altair.app.ticketing.tickets.utils import build_dicts_from_ordered_product_item
        expected = {
            u"organization": {
                u"name": u"組織名",
                u"code": u"RT"
                },
            u"event": {
                u"code": u"RTTST",
                u"title": u"イベント名",
                u"abbreviated_title": u"イベント名略称"
                },
            u"performance": {
                u"name": u"パフォーマンス名",
                u"code": u"RTTST0000000",
                u"open_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 10, u"minute": 1, u"second": 2, 
                    u"weekday": 0, 
                    },
                u"start_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 11, u"minute": 3, u"second": 4, 
                    u"weekday": 0, 
                    },
                u"end_on": None, 
                },
            u"venue": {
                u"name": u"会場名",
                u"sub_name": u"サブ会場名"
                },
            u"stock": {
                u"quantity": 100
                },
            u"stockStatus": {
                u"quantity": 98,
                },
            u"stockHolder": {
                u"name": u"stock_holder"
                },
            u"stockType": {
                u"name": u"S席",
                u"type": 0,
                u"display_order": 0,
                u"quantity_only": 0
                },
            u"seat": {
                u"l0_id": u"l0_id",
                u"name": u"seat_name",
                u"seat_no": u"seat_no"
                },
            u"イベント名": u"イベント名",
            u"パフォーマンス名": u"パフォーマンス名",
            u"対戦名": u"パフォーマンス名",
            u"会場名": u"会場名",
            u"公演コード": u"RTTST0000000",
            u"開催日": u"2012年 12月 31日 (月)",
            u"開場時刻": u"10時 01分",
            u"開場時刻s": u"10:01",
            u"開始時刻": u"11時 03分",
            u"開始時刻s": u"11:03",
            u"終了時刻": u"",
            u"席種名": u"S席",
            u"席番": u"seat_name",
            u"注文番号": u"000000000000",
            u"注文日時": u"2012年 10月 30日 (火) 12時 34分",
            u"注文日時s": u"2012/10/30 (火) 12:34",
            u"受付番号": u"000000000000",
            u"受付日時": u"2012年 10月 30日 (火) 12時 34分",
            u"受付日時s": u"2012/10/30 (火) 12:34",
            u"発券日時": u"2012年 11月 01日 (木) 12時 34分",
            u"発券日時s": u"2012/11/01 (木) 12:34",
            u"発券番号": None,
            }
        out = build_dicts_from_ordered_product_item(self.order.items[0].ordered_product_items[0])
        self.assertEqual(1, len(out))
        self.assertEqual(self.seat, out[0][0])
        for k in expected:
            self.assertEqual(expected[k], out[0][1][k], (u"%s: expected %s, got %s" % (k, expected[k], out[0][1][k])).encode('utf-8'))

    def test_build_dicts_from_carted_product_item(self):
        from altair.app.ticketing.tickets.utils import build_dicts_from_carted_product_item
        expected = {
            u"organization": {
                u"name": u"組織名",
                u"code": u"RT"
                },
            u"event": {
                u"code": u"RTTST",
                u"title": u"イベント名",
                u"abbreviated_title": u"イベント名略称"
                },
            u"performance": {
                u"name": u"パフォーマンス名",
                u"code": u"RTTST0000000",
                u"open_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 10, u"minute": 1, u"second": 2, 
                    u"weekday": 0, 
                    },
                u"start_on": {
                    u"year": 2012, u"month": 12, u"day": 31,
                    u"hour": 11, u"minute": 3, u"second": 4, 
                    u"weekday": 0, 
                    },
                u"end_on": None, 
                },
            u"venue": {
                u"name": u"会場名",
                u"sub_name": u"サブ会場名"
                },
            u"stock": {
                u"quantity": 100
                },
            u"stockStatus": {
                u"quantity": 98,
                },
            u"stockHolder": {
                u"name": u"stock_holder"
                },
            u"stockType": {
                u"name": u"S席",
                u"type": 0,
                u"display_order": 0,
                u"quantity_only": 0
                },
            u"seat": {
                u"l0_id": u"l0_id",
                u"name": u"seat_name",
                u"seat_no": u"seat_no"
                },
            u"イベント名": u"イベント名",
            u"パフォーマンス名": u"パフォーマンス名",
            u"対戦名": u"パフォーマンス名",
            u"会場名": u"会場名",
            u"公演コード": u"RTTST0000000",
            u"開催日": u"2012年 12月 31日 (月)",
            u"開場時刻": u"10時 01分",
            u"開場時刻s": u"10:01",
            u"開始時刻": u"11時 03分",
            u"開始時刻s": u"11:03",
            u"終了時刻": u"",
            u"席種名": u"S席",
            u"席番": u"seat_name",
            u"注文番号": u"000000000000",
            u"注文日時": u"2012年 10月 30日 (火) 12時 34分",
            u"注文日時s": u"2012/10/30 (火) 12:34",
            u"受付番号": u"000000000000",
            u"受付日時": u"2012年 10月 30日 (火) 12時 34分",
            u"受付日時s": u"2012/10/30 (火) 12:34",
            u"発券日時": u"\ufeff{{発券日時}}\ufeff",
            u"発券日時s": u"\ufeff{{発券日時s}}\ufeff",
            u"発券番号": None,
            }
        out = build_dicts_from_carted_product_item(self.cart.products[0].items[0], now=datetime(2012, 10, 30, 12, 34, 56))
        self.assertEqual(1, len(out))
        self.assertEqual(self.seat, out[0][0])
        for k in expected:
            self.assertEqual(expected[k], out[0][1][k], (u"%s: expected %s, got %s" % (k, expected[k], out[0][1][k])).encode('utf-8'))

class TicketsCleanerTest(TestCase):
    def testTransformApplier(self):
        from altair.app.ticketing.tickets.cleaner import TransformApplier
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="10" height="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(10, float(elem.get(u'x')))
        self.assertEqual(20, float(elem.get(u'y')))
        self.assertEqual(20, float(elem.get(u'width')))
        self.assertEqual(20, float(elem.get(u'height')))

        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><circle cx="10" cy="10" r="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(30, float(elem.get(u'cx')))
        self.assertEqual(40, float(elem.get(u'cy')))
        self.assertEqual(10, float(elem.get(u'r')))

        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><line x1="20" y1="10" x2="0" y2="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        self.assertEqual(40, float(elem.get(u'x1')))
        self.assertEqual(50, float(elem.get(u'y1')))
        self.assertEqual(20, float(elem.get(u'x2')))
        self.assertEqual(30, float(elem.get(u'y2')))

        from altair.app.ticketing.tickets.utils import parse_poly_data
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><polyline points="1,2 3,4 5,6" transform="matrix(1, 1, 1, 1, 10, 20)" /></svg>''')
        TransformApplier()(svg)
        elem = svg[0]
        points = list(parse_poly_data(elem.get(u'points')))
        self.assertEqual(3, len(points))
        self.assertEqual((13., 23.), points[0])
        self.assertEqual((17., 27.), points[1])
        self.assertEqual((21., 31.), points[2])

    def testTransformApplierNested(self):
        from altair.app.ticketing.tickets.cleaner import TransformApplier
        svg = etree.fromstring('''<svg xmlns="http://www.w3.org/2000/svg"><g transform="translate(10, 20)"><g transform="matrix(1, 1, 1, 1, 0, 0)"><rect x="0" y="0" width="10" height="10" transform="matrix(1, 1, 1, 1, 10, 20)" /></g></g></svg>''')
        TransformApplier()(svg)
        elem = svg[0][0][0]
        self.assertEqual(40, float(elem.get(u'x')))
        self.assertEqual(50, float(elem.get(u'y')))
        self.assertEqual(40, float(elem.get(u'width')))
        self.assertEqual(40, float(elem.get(u'height')))

