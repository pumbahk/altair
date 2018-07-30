# encoding: utf-8

import mock
import re
import unittest

from decimal import Decimal
from pyramid import testing
from datetime import datetime
from altair.app.ticketing.core.testing import CoreTestMixin
from altair.app.ticketing.testing import _setup_db, _teardown_db

from altair.app.ticketing.cart.models import CartSetting
from altair.app.ticketing.core.models import (
    Organization,
    OrganizationSetting,
    Host,
    Event,
    EventSetting,
    Performance,
    Venue,
    Site,
    PaymentMethod,
    DeliveryMethod,
    PaymentMethodPlugin,
    DeliveryMethodPlugin,
    Stock,
    StockStatus,
    StockHolder,
    StockType,
    StockTypeEnum,
    SalesSegmentGroup,
    SalesSegment,
    Product,
    ProductItem,
    ShippingAddress
)
from altair.app.ticketing.payments import plugins as _plugins
from altair.app.ticketing.operators.models import Operator
from altair.app.ticketing.users.models import (
    Membership,
    MemberGroup,
    Member,
    User,
    UserCredential
)

from .models import (OrderImportTask,
                     ImportTypeEnum,
                     ImportStatusEnum,
                     AllocationModeEnum,
                     Order)
from .importer import run_import_task

DEFAULT_BASIC = {
    u'order.order_no': u'予約番号',
    u'order.status': u'ステータス',
    u'order.payment_status': u'決済ステータス',
    u'order.created_at': u'',
    u'order.paid_at': u'',
    u'order.delivered_at': u'配送日時',
    u'order.canceled_at': u'キャンセル日時',
    u'order.total_amount': u'110',
    u'order.transaction_fee': u'30',
    u'order.delivery_fee': u'20',
    u'order.system_fee': u'10',
    u'order.special_fee': u'40',
    u'order.margin': u'内手数料金額',
    u'order.note': u'メモ',
    u'order.special_fee_name': u'特別手数料名',
    u'payment_method.name': u'RESERVE_NUMBER',
    u'delivery_method.name': u'RESERVE_NUMBER',
    u'event.title': u'イベント',
    u'performance.name': u'パフォーマンス',
    u'performance.code': u'XXIMPRT0101Z',
    u'venue.name': u'会場',
    u'mail_magazine.mail_permission': u'メールマガジン受信可否',
    u'ordered_product_item.print_histories': u'発券作業者',
    u'ordered_product.product.sales_segment.sales_segment_group.name': u'存在する販売区分グループ',
    u'ordered_product.product.sales_segment.margin_ratio': u'販売手数料率',
}

DEFAULT_SHIPPING_ADDRESS = {
    u'shipping_address.last_name': u'配送先姓',
    u'shipping_address.first_name': u'配送先名',
    u'shipping_address.last_name_kana': u'配送先姓(カナ)',
    u'shipping_address.first_name_kana': u'配送先名(カナ)',
    u'shipping_address.zip': u'郵便番号',
    u'shipping_address.country': u'国',
    u'shipping_address.prefecture': u'都道府県',
    u'shipping_address.city': u'市区町村',
    u'shipping_address.address_1': u'住所1',
    u'shipping_address.address_2': u'住所2',
    u'shipping_address.tel_1': u'電話番号1',
    u'shipping_address.tel_2': u'電話番号2',
    u'shipping_address.fax': u'FAX',
    u'shipping_address.email_1': u'メールアドレス1',
    u'shipping_address.email_2': u'メールアドレス2'
}

ORDERED_SHIPPING_ADDRESS = {
    u"shipping_address.first_name": u"太郎0",
    u"shipping_address.last_name": u"楽天",
    u"shipping_address.first_name_kana": u"タロウ",
    u"shipping_address.last_name_kana" :u"ラクテン",
    u"shipping_address.zip": u"251-0036",
    u"shipping_address.country": u"日本",
    u"shipping_address.prefecture": u"東京都",
    u"shipping_address.city": u"品川区",
    u"shipping_address.address_1": u"東五反田5-21-15",
    u"shipping_address.address_2": u"メタリオンOSビル",
    u"shipping_address.tel_1": u"03-9999-9999",
    u"shipping_address.tel_2": u"090-0000-0000",
    u"shipping_address.fax": u"03-9876-5432",
    u"shipping_address.email_1": u"dev+test000@ticketstar.jp",
    u"shipping_address.email_2": u"dev+mobile-test000@ticketstar.jp",
}

DEFAULT_USER = {
    u'user_profile.last_name': u'姓',
    u'user_profile.first_name': u'名',
    u'user_profile.last_name_kana': u'姓(カナ)',
    u'user_profile.first_name_kana': u'名(カナ)',
    u'user_profile.nick_name': u'ニックネーム',
    u'user_profile.sex': u'性別',
    u'membership.name': u'会員種別名',
    u'membergroup.name': u'会員グループ名',
    u'user_credential.authz_identifier': u'user1',
}

DEFAULT_ATTRIBUTION = {
    u'attribute[aaa]': u'bbb',
    u'attribute[bbb]': u'ccc'
}

def _get_test_data(product, shipping_address=None, user=None, attr_data=None, update_data=None):
    test_data = DEFAULT_BASIC.copy()

    test_data.update(product)

    if shipping_address:
        test_data.update(shipping_address)
    else:
        test_data.update(DEFAULT_SHIPPING_ADDRESS)

    if user:
        test_data.update(user)
    else:
        test_data.update(DEFAULT_USER)

    if attr_data:
        test_data.update(attr_data)
    else:
        test_data.update(DEFAULT_ATTRIBUTION)

    if update_data:
        test_data.update(update_data)

    return test_data

def get_data_with_seat(name, quantity, ticket_idx, price=10, item_quantity=None, item_price=None, item_suffix=None, seat_prefix=None, attr_data=None, update_data=None):
    if not seat_prefix:
        seat_prefix = name.split(u'-')[0]

    product = {
        u'ordered_product.product.name': u'%s' % name,
        u'ordered_product.price': u'%d' % price,
        u'ordered_product.quantity': u'%d' % quantity,
        u'ordered_product_item.product_item.name': u'%s-%s' % (name, item_suffix or u'0'),
        u'ordered_product_item.price': u'%d' % (item_price or price),
        u'ordered_product_item.quantity': u'%d' % (item_quantity or 1),
        u'seat.name': u'Seat %s-%d' % ((seat_prefix or name), ticket_idx)
    }

    if quantity > 1:
        new_total_amount = 100 + price * quantity
        product.update({
            u'order.total_amount': u'%d' % new_total_amount,
        })
    test_data = _get_test_data(product, attr_data=attr_data, update_data=update_data)
    return test_data

def get_data_without_seat(name, quantity, price=10, item_suffix=None, item_quantity=None, item_price=None, attr_data=None, update_data=None):
    product = {
        u'ordered_product.product.name': u'%s' % name,
        u'ordered_product.price': u'%d' % price,
        u'ordered_product.quantity': u'%d' % quantity,
        u'ordered_product_item.product_item.name': u'%s-%s' % (name, item_suffix or u'0'),
        u'ordered_product_item.price': u'%d' % (item_price or price),
        u'ordered_product_item.quantity': u'%d' % (item_quantity or 1),
    }

    if quantity > 1:
        new_total_amount = 100 + price * quantity
        product.update({
            u'order.total_amount': u'%d' % new_total_amount,
        })
    test_data = _get_test_data(product, attr_data=attr_data, update_data=update_data)
    return test_data

def get_data_with_customized_product(product, update_data=None):
    test_data = _get_test_data(product, update_data=update_data)
    return test_data

def get_data_existing_order(order, update_data=None, with_attr=True):
    base_data = DEFAULT_BASIC.copy()
    base_data.update(ORDERED_SHIPPING_ADDRESS)
    base_data.update(DEFAULT_USER)
    base_data[u'order.order_no'] = order.order_no
    base_data[u'order.total_amount'] = str(order.total_amount)
    base_data[u'payment_method.name'] = order.payment_delivery_pair.payment_method.name
    base_data[u'delivery_method.name'] = order.payment_delivery_pair.delivery_method.name
    if order.user:
        base_data[u'user_credential.authz_identifier'] = order.user.user_credential[0].authz_identifier

    if with_attr and order.attributes:
        attr_data = {u'attribute[%s]' % k: v for k, v in order.attributes.items()}
        base_data.update(attr_data)

    output = []

    for item in order.items:
        for elem in item.elements:
            product = {
                u'ordered_product.product.name': unicode(item.product.name),
                u'ordered_product.price': unicode(item.price),
                u'ordered_product.quantity': unicode(item.quantity),
                u'ordered_product_item.product_item.name': unicode(elem.product_item.name),
                u'ordered_product_item.price': unicode(elem.price),
                u'ordered_product_item.quantity': unicode(elem.product_item.quantity),
            }
            if elem.seats:
                for seat in elem.seats:
                    product.update({
                        u'seat.name': unicode(seat.name)
                    })
                    _tmp = base_data.copy()
                    _tmp.update(product)

                    if update_data:
                        _tmp.update(update_data)

                    output.append(_tmp)
            else:
                for _ in range(elem.quantity):
                    _tmp = base_data.copy()
                    _tmp.update(product)

                    if update_data:
                        _tmp.update(update_data)

                    output.append(_tmp)

    return output

class ImportBaseTestMixin(CoreTestMixin):

    def _build_core_models(self):
        self.organization = Organization(id=1, short_name=u'', code=u'XX')
        self.host = Host(organization=self.organization, host_name='example.com:80')
        self._create_cart_settings()
        self.organization.settings = [OrganizationSetting(cart_setting=self.cart_settings[0])]
        self.operator = Operator()
        self.session.add(self.operator)
        self._create_payment_delivery_methods()
        self._create_membergroup()
        self._create_users_with_member(auth_identifier='user1')
        self._create_users_with_member(auth_identifier='user2')

        self.event = Event(organization=self.organization, title=u'イベント')
        self.another_event = Event(organization=self.organization, title=u'他のイベント')

        self.stock_types = self._create_stock_types()
        self.sales_segment_group = SalesSegmentGroup(name=u'存在する販売区分グループ', event=self.event)
        self.payment_delivery_method_pairs = self._create_payment_delivery_method_pairs(
            self.sales_segment_group,
            transaction_fee=30,
            delivery_fee_per_order=20,
            delivery_fee_per_principal_ticket=0,
            delivery_fee_per_subticket=0,
            system_fee=10,
            special_fee=40)

        self.performance, self.stocks, self.seats, self.sales_segment, self.products = \
            self._create_performance_with_product(
            event=self.event,
            name=u'パフォーマンス',
            code=u'XXIMPRT0101Z',
            start_on=datetime(2018, 1, 1),
            stock_types=self.stock_types,
            sales_segment_group=self.sales_segment_group,
            payment_delivery_method_pairs=self.payment_delivery_method_pairs
        )

        self.another_performance, self.another_stocks, self.another_seats, self.another_sales_segment, self.another_products = \
            self._create_performance_with_product(
            event=self.event,
            name=u'パフォーマンス',
            code=u'XXIMPRT0101X',
            start_on=datetime(2018, 1, 1),
            stock_types=self.stock_types,
            sales_segment_group=self.sales_segment_group,
            payment_delivery_method_pairs=self.payment_delivery_method_pairs
        )

        self.existing_orders = [
            # 座席あり
            self._create_order(
                [(self.products[0], 2)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000000'
            ),
            # 座席あり
            self._create_order(
                [(self.products[0], 2), (self.products[1], 1)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000001'
            ),
            # 数受け
            self._create_order(
                [(self.products[4], 2)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000002'
            ),
            # 数受け
            self._create_order(
                [(self.products[4], 2), (self.products[5], 1)],
                self.sales_segment,
                self.payment_delivery_method_pairs[0],
                order_no='YY0000000003'
            ),
        ]
        self.existing_orders[0].attributes[u'key1'] = u'value1'
        self.existing_orders[0].attributes[u'key2'] = u'value2'

        self.session.flush()

    def _create_cart_settings(self):
        self.cart_settings = [
            CartSetting(
                organization=self.organization,
                name=u'default'
            ),
            CartSetting(
                organization=self.organization,
                name=u'event'
            ),
            CartSetting(
                organization=self.organization,
                name=u'another_event'
            ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
            ),
            CartSetting(
                organization=self.organization,
                name=u'duplicate'
            ),
        ]
        for cart_setting in self.cart_settings:
            self.session.add(cart_setting)

    def _create_membergroup(self):
        self.membership = Membership(organization=self.organization, name=u'会員種別名')
        self.session.add(self.membership)
        self.membergroup = MemberGroup(membership=self.membership, name=u'会員グループ名')
        self.session.add(self.membergroup)

    def _create_user(self, auth_identifier):
        user = User(
            user_credential=[
                UserCredential(
                    auth_identifier=auth_identifier,
                    authz_identifier=auth_identifier,
                    membership=self.membership
                )
            ]
        )
        self.session.add(user)
        if hasattr(self, 'users'):
            self.users.append(user)
        else:
            self.users = [user]

    def _create_member(self, auth_identifier):
        member = Member(
            auth_identifier=auth_identifier,
            membership=self.membership,
            membergroup=self.membergroup
        )
        self.session.add(member)
        if hasattr(self, 'members'):
            self.members.append(member)
        else:
            self.members = [member]

    def _create_users_with_member(self, auth_identifier):
        self._create_user(auth_identifier)
        self._create_member(auth_identifier)

    def _create_payment_delivery_methods(self):
        payment_methods = {}
        delivery_methods = {}
        for attr_name in dir(_plugins):
            g = re.match(ur'^(.*)_PAYMENT_PLUGIN_ID$', attr_name)
            if g:
                id = getattr(_plugins, attr_name)
                name = g.group(1)
                payment_methods[id] = \
                    PaymentMethod(
                        name=name, fee=Decimal(0.),
                        organization=self.organization,
                        payment_plugin_id=id,
                        _payment_plugin=PaymentMethodPlugin(id=id, name=name)
                    )
            else:
                g = re.match(ur'^(.*)_DELIVERY_PLUGIN_ID$', attr_name)
                if g:
                    id = getattr(_plugins, attr_name)
                    name = g.group(1)
                    delivery_methods[id] = \
                        DeliveryMethod(
                            name=name,
                            fee_per_order=Decimal(0.),
                            fee_per_principal_ticket=Decimal(0.),
                            fee_per_subticket=Decimal(0.),
                            organization=self.organization,
                            delivery_plugin_id=id,
                            _delivery_plugin=DeliveryMethodPlugin(id=id, name=name)
                        )
        self.payment_methods = payment_methods
        self.delivery_methods = delivery_methods

    def _create_stock_types(self, *args, **kwargs):
        return [
            # products[0][1]
            StockType(name=u'A', type=StockTypeEnum.Seat.v, quantity_only=False),
            # products[2][3]
            StockType(name=u'B', type=StockTypeEnum.Seat.v, quantity_only=False),
            # products[4][5]
            StockType(name=u'C', type=StockTypeEnum.Seat.v, quantity_only=True),
            # products[6][7]
            StockType(name=u'D', type=StockTypeEnum.Seat.v, quantity_only=True)
        ]

    def _create_performance_with_product(self, event, name, code, start_on, stock_types, sales_segment_group, payment_delivery_method_pairs):
        performance = Performance(
            start_on=start_on,
            event=event,
            venue=Venue(organization=self.organization, site=Site()),
            name=name,
            code=code
        )
        stocks = self._create_stocks(performance, stock_types, 20)
        seats = self._create_seats(stocks)
        seat_adjacency_sets = self._create_seat_adjacency_sets(seats)
        for seat_adjacency_set in seat_adjacency_sets:
            self.session.add(seat_adjacency_set)
        sales_segment = SalesSegment(
            sales_segment_group=sales_segment_group,
            payment_delivery_method_pairs=payment_delivery_method_pairs,
            performance=performance
        )
        products = []
        for stock in stocks:
            for name in [u'A', u'B']:
                if name == u'A':
                    price = 100
                else:
                    price = 50
                products.append(
                    self._create_product(name, price, stock, 1, performance, sales_segment)
                )

        return performance, stocks, seats, sales_segment, products

    def _create_stocks(self, performance, stock_types, quantity=4):
        return [Stock(performance=performance,
                      stock_type=stock_type,
                      quantity=quantity,
                      stock_holder=StockHolder(name='holder of %s' % stock_type.name),
                      stock_status=StockStatus(quantity=quantity))
                for stock_type in stock_types]

    def _create_product(self, name, price, stock, quantity, performance, sales_segment):
        """
        name = u'A', price = 100, quantity = 1, stock.stock_type.name=u'B'
        Product.name = u'B-A'
        Product.price = 100
        ProductItem.name = u'B-A-0'
        ProductItem.price = 100

        name = u'A', price = 100, quantity = 2, stock.stock_type.name=u'B'
        Product.name = u'B-A'
        Product.price = 100
        1.
        ProductItem.name = u'B-A-0'
        ProductItem.price = 50
        ２.
        ProductItem.name = u'B-A-1'
        ProductItem.price = 50

        :param name: str
        :param price: int
        :param stock: Stock
        :param quantity: int
        :param performance: Performance
        :param sales_segment: SalesSegment
        :return: list
        """
        price = Decimal(price)
        item_price = Decimal(price//quantity)
        return Product(
            name=u'%s-%s' % (stock.stock_type.name, name),
            price=price,
            performance=performance,
            sales_segment=sales_segment,
            items = [
                ProductItem(
                    name=u'%s-%s-%d' % (stock.stock_type.name, name, i),
                    stock=stock,
                    price=item_price,
                    performance=performance,
                    quantity=quantity,
                    ticket_bundle=self._create_ticket_bundle()
                ) for i in range(quantity)
            ]
        )

    def _pick_seats(self, stock, quantity):
        from altair.app.ticketing.core.models import SeatStatusEnum
        assert stock in self.stocks

        result = []
        for seat in self.seats:
            if seat.stock == stock and seat.status == SeatStatusEnum.Vacant.v:
                result.append(seat)
                if len(result) == quantity:
                    break
        else:
            assert False, 'len(result) < quantity'
        return result

    def _create_shipping_address(self):
        # ticketing.CoreTestMixinの方法でShippingAddressの中でcountryが入ってない。
        return ShippingAddress(
            email_1="dev+test000@ticketstar.jp",
            email_2="dev+mobile-test000@ticketstar.jp",
            first_name=u"太郎0",
            last_name=u"楽天",
            first_name_kana=u"タロウ",
            last_name_kana=u"ラクテン",
            zip=u"251-0036",
            country=u"日本",
            prefecture=u"東京都",
            city=u"品川区",
            address_1=u"東五反田5-21-15",
            address_2=u"メタリオンOSビル",
            tel_1=u"03-9999-9999",
            tel_2=u"090-0000-0000",
            fax=u"03-9876-5432"
            )

    def _create_order(self, product_quantity_pairs, sales_segment=None, pdmp=None, order_no=None, cart_setting_id=None):
        order = super(ImportBaseTestMixin, self)._create_order(product_quantity_pairs,
                                                               sales_segment,
                                                               pdmp,
                                                               order_no,
                                                               cart_setting_id)
        # ticketing.CoreTestMixinの方法で予約金額の総数にシステム手数料を入ってない。
        order.total_amount += order.system_fee
        return order

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def _getTarget(self):
        raise NotImplementedError()

    def setUp(self):
        self.request = testing.DummyRequest()
        self.session = _setup_db(
            modules=[
                'altair.app.ticketing.core.models',
                'altair.app.ticketing.lots.models',
                'altair.app.ticketing.orders.models',
                'altair.app.ticketing.users.models',
                'altair.app.ticketing.operators.models',
                ]
            )

        self._build_core_models()

class ImportCSVParserTest(ImportBaseTestMixin, unittest.TestCase):
    def _getTarget(self):
        from .importer import ImportCSVParser
        return ImportCSVParser

    def setUp(self):
        super(ImportCSVParserTest, self).setUp()

        self.membergroup.sales_segments.append(self.sales_segment)
        self.existing_orders[1].membership = self.membership
        self.existing_orders[1].user = self.users[1]
        self.session.flush()
        self.config = testing.setUp(settings={
            'altair.cart.completion_page.temporary_store.cookie_name': 'xxx',
            'altair.cart.completion_page.temporary_store.secret': 'xxx',
            })
        self.config.include('altair.app.ticketing.cart.setup_components')

    def tearDown(self):
        testing.tearDown()
        _teardown_db()

    def get_order_import_task(self, import_type, allocation_mode):
        task = OrderImportTask()
        task.organization = self.organization
        task.operator = self.operator
        task.import_type = import_type
        task.allocation_mode = allocation_mode
        task.status = ImportStatusEnum.Waiting.v
        task.count = 0

        return task
    
    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_seat_no_errors(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0),
            get_data_with_seat(u'A-B', 1, 0),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_methods[_plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.delivery_methods[_plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(proto_order.attributes[u'aaa'], u'bbb')
        self.assertEqual(proto_order.attributes[u'bbb'], u'ccc')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_seat_with_wrong_allocation_mode(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.NoAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0)
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[u'予約番号'].message,
                         u'配席モードは「数受けのため配席しない」ですが、インポート先の席種「A」は数受けではありません。')


    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_quantity_only_no_errors(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.NoAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_without_seat(u'C-A', 1, 0),
            get_data_without_seat(u'C-B', 1, 0),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[4])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[4].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 0)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[5])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[5].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 0)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method,
                         self.payment_methods[_plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method,
                         self.delivery_methods[_plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name, u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name, u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana, u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana, u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip, u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country, u'国')
        self.assertEqual(proto_order.shipping_address.prefecture, u'都道府県')
        self.assertEqual(proto_order.shipping_address.city, u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1, u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2, u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1, u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2, u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax, u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1, u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2, u'メールアドレス2')
        self.assertEqual(proto_order.attributes[u'aaa'], u'bbb')
        self.assertEqual(proto_order.attributes[u'bbb'], u'ccc')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_quantity_only_with_wrong_allocation_mode(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'C-A', 1, 0)
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[u'予約番号'].message,
                         u'配席モードは「座席番号に該当する座席を配席する」ですが、インポート先の席種「C」は数受けです。')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_quantity_only_with_wrong_allocation_mode_2(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.ReAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'C-A', 1, 0)
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[u'予約番号'].message,
                         u'配席モードは「座席番号を無視し常に自動配席する」ですが、インポート先の席種「C」は数受けです。')

    def test_create_fail_attributes_differ_amongst_the_entries_of_the_same_key(self):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0),
            get_data_with_seat(u'A-B', 1, 0, attr_data={u'attribute[aaa]': u'bbb'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'同じキーを持つエントリの間で属性値に相違があります')
        self.assertEqual(len(proto_orders), 0)

    def test_create_fail_with_multiple_performance_candidate(self):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'performance.code': u'', u'performance.start_on': u''}),
            get_data_with_seat(u'A-B', 1, 0, update_data={u'performance.code': u'', u'performance.start_on': u''}),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'複数の候補があります  公演名: パフォーマンス, 公演コード: , 公演日: ')
        self.assertEqual(len(proto_orders), 0)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_with_performance_date_specified(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        get_next_order_no.return_value = 'XX0000000000'
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'performance.code': u'XXIMPRT0101Z',
                                                          u'performance.start_on': u'2018/01/01 00:00:00'}),
            get_data_with_seat(u'A-B', 1, 0, update_data={u'order.order_no': u'XX',
                                                          u'performance.code': u'XXIMPRT0101Z',
                                                          u'performance.start_on': u'2018-01-01 01:00:00'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'XX'].message, u'公演日が違います  公演名: パフォーマンス, 公演コード: XXIMPRT0101Z, 公演日: 2018-01-01 01:00:00 != 2018年1月1日 0:00:00')
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 1)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_methods[_plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.delivery_methods[_plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

    def test_create_with_product_invalid_product_item(self):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, item_suffix=u'3'),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'商品明細がありません  商品明細: A-A-3')
        self.assertEqual(len(proto_orders), 0)

    def test_create_with_product_without_product_item(self):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        product_z = Product(
            name='A-Z',
            price=1,
            performance=self.performance,
            sales_segment=self.sales_segment,
            items=[]
            )
        self.session.add(product_z)
        self.session.flush()
        test_data = [
            get_data_with_seat(u'A-Z', 1, 0, item_suffix=u'0'),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'商品明細がありません  商品明細: A-Z-0')
        self.assertEqual(len(proto_orders), 0)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_with_product_with_null_quantity(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'ordered_product.quantity': u''}),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'商品個数が指定されていません')
        self.assertEqual(len(proto_orders), 0)

    def test_create_with_product_item_with_null_quantity(self):
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'ordered_product_item.quantity': u''}),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'商品明細個数が指定されていません')
        self.assertEqual(len(proto_orders), 0)

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_with_product_item_having_multiple_unit(self, get_next_order_no):
        set_product = self._create_product(name=u'Z', price=10, performance=self.performance, stock=self.stocks[0], quantity=2, sales_segment=self.sales_segment)
        self.session.add(set_product)
        get_next_order_no.return_value = 'XX0000000000'
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'2',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-0'
                }
            ),
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'2',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-1'
                }
            ),
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'2',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-2'
                }
            ),
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'2',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-3'
                }
            )
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 1)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        proto_order = iter(proto_orders.values()).next()
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'XX0000000000')
        self.assertEqual(len(proto_order.items), 1)
        self.assertEqual(proto_order.items[0].product, set_product)
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, set_product.items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 4)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 4)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_methods[_plugins.RESERVE_NUMBER_PAYMENT_PLUGIN_ID])
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.delivery_methods[_plugins.RESERVE_NUMBER_DELIVERY_PLUGIN_ID])
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(proto_order.attributes[u'aaa'], u'bbb')
        self.assertEqual(proto_order.attributes[u'bbb'], u'ccc')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
    
    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_create_fail_with_product_item_having_multiple_unit_too_many_entries(self, get_next_order_no):
        set_product = self._create_product(name=u'Z', price=10, performance=self.performance, stock=self.stocks[0], quantity=2, sales_segment=self.sales_segment)
        self.session.add(set_product)
        get_next_order_no.return_value = 'XX0000000000'
        task = self.get_order_import_task(ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'1',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-0'
                }
            ),
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'1',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-1'
                }
            ),
            get_data_with_customized_product(
                product={
                    u'ordered_product.quantity': u'1',
                    u'ordered_product_item.price': u'5',
                    u'ordered_product.product.name': u'A-Z',
                    u'ordered_product_item.quantity': u'1',
                    u'ordered_product_item.product_item.name': u'A-Z-0',
                    u'seat.name': u'Seat A-2'
                }
            )
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'商品「A-Z」の商品明細「A-Z-0」の数量 2 × 商品個数 1 を超える数のデータが存在します')
        self.assertEqual(len(proto_orders), 0)

    def test_update_non_existent(self):
        task = self.get_order_import_task(ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'更新対象もしくは移動対象の予約が存在しません。')

    def test_update_diff_performance_fail(self):
        task = self.get_order_import_task(ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.another_performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0,
                               update_data={u'order.order_no': u'YY0000000000', u'performance.code': u'XXIMPRT0101X'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertIn('YY0000000000', errors)
        self.assertEqual(errors['YY0000000000'].message, u'インポート方法が「予約を更新」の場合は同じパフォーマンスでインポートを行ってください。')

    def test_update_different_payment_method(self):
        task = self.get_order_import_task(ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'order.order_no': u'YY0000000000',
                                                        u'payment_method.name': u'RESERVE_NUMBER'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の決済方法と新しい注文の決済方法が異なっています。')

    def test_update_different_delivery_method(self):
        task = self.get_order_import_task(ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'order.order_no': u'YY0000000000',
                                                        u'payment_method.name': self.existing_orders[
                                                            0].payment_delivery_pair.payment_method.name,
                                                        u'delivery_method.name': u'RESERVE_NUMBER'})
        ]
        proto_orders, errors = target(test_data)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の引取方法と新しい注文の引取方法が異なっています。')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_update(self, get_next_order_no):
        task = self.get_order_import_task(ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({u'order.total_amount': u'250'})
        test_data_1 = get_data_existing_order(self.existing_orders[0], update_data=DEFAULT_SHIPPING_ADDRESS)
        product = {
            u'ordered_product.product.name': u'A-B',
            u'ordered_product.price': u'50',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-B-0',
            u'ordered_product_item.price': u'50',
            u'ordered_product_item.quantity': u'1',
            u'seat.name': u'Seat A-5'
        }
        test_data_1[1].update(product)
        test_data_2 = get_data_existing_order(self.existing_orders[1], with_attr=False)
        proto_orders, errors = target(test_data_1 + [test_data_2[0]])
        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 2)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity

        _proto_orders = list(proto_orders.values())
        proto_order = _proto_orders[0]
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'YY0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_delivery_method_pairs[0].payment_method)
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.payment_delivery_method_pairs[0].delivery_method)
        self.assertEqual(proto_order.shipping_address.last_name,  u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name,  u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip,  u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country,  u'国')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'都道府県')
        self.assertEqual(proto_order.shipping_address.city,  u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1,  u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2,  u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax,  u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1,  u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2,  u'メールアドレス2')
        self.assertEqual(proto_order.attributes['key1'], 'value1')
        self.assertEqual(proto_order.attributes['key2'], 'value2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

        proto_order = _proto_orders[1]
        self.assertEqual(proto_order.order_no, 'YY0000000001')
        self.assertEqual(len(proto_order.items), 1)
        self.assertEqual(proto_order.items[0].product, self.products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method, self.payment_delivery_method_pairs[0].payment_method)
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method, self.payment_delivery_method_pairs[0].delivery_method)
        self.assertEqual(proto_order.shipping_address.last_name,  u'楽天')
        self.assertEqual(proto_order.shipping_address.first_name,  u'太郎0')
        self.assertEqual(proto_order.shipping_address.last_name_kana,  u'ラクテン')
        self.assertEqual(proto_order.shipping_address.first_name_kana,  u'タロウ')
        self.assertEqual(proto_order.shipping_address.zip,  u'2510036')
        self.assertEqual(proto_order.shipping_address.country,  u'日本')
        self.assertEqual(proto_order.shipping_address.prefecture,  u'東京都')
        self.assertEqual(proto_order.shipping_address.city,  u'品川区')
        self.assertEqual(proto_order.shipping_address.address_1,  u'東五反田5-21-15')
        self.assertEqual(proto_order.shipping_address.address_2,  u'メタリオンOSビル')
        self.assertEqual(proto_order.shipping_address.tel_1,  u'03-9999-9999')
        self.assertEqual(proto_order.shipping_address.tel_2,  u'090-0000-0000')
        self.assertEqual(proto_order.shipping_address.fax,  u'03-9876-5432')
        self.assertEqual(proto_order.shipping_address.email_1,  u'dev+test000@ticketstar.jp')
        self.assertEqual(proto_order.shipping_address.email_2,  u'dev+mobile-test000@ticketstar.jp')
        self.assertEqual(proto_order.membership,  self.existing_orders[1].membership)
        self.assertEqual(proto_order.membergroup, self.membergroup)
        self.assertEqual(proto_order.attributes, {})
        self.assertEqual(proto_order.user, self.existing_orders[1].user)

    def test_transfer_non_existent(self):
        task = self.get_order_import_task(ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0),
        ]
        proto_orders, errors = target(test_data)
        self.assertEqual(errors[u'予約番号'].message, u'更新対象もしくは移動対象の予約が存在しません。')

    def test_transfer_same_performance_fail(self):
        task = self.get_order_import_task(ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, task, self.organization, performance=self.performance)
        test_data = [
            get_data_with_seat(u'A-A', 1, 0, update_data={u'order.order_no': u'YY0000000000'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertIn('YY0000000000', errors)
        self.assertEqual(errors['YY0000000000'].message, u'インポート方法が「予約の移動」の場合は違うパフォーマンスで行ってください。')

    def test_transfer_different_payment_method(self):
        _task = self.get_order_import_task(ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, _task, self.organization,
                               performance=self.another_performance)
        test_data = [
            get_data_with_seat(u'A', 1, 0, update_data={u'order.order_no': u'YY0000000000',
                                                        u'performance.code': u'XXIMPRT0101X',
                                                        u'payment_method.name': u'RESERVE_NUMBER'}),
        ]
        proto_orders, errors = target(test_data)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の決済方法と新しい注文の決済方法が異なっています。')

    def test_transfer_different_delivery_method(self):
        _task = self.get_order_import_task(ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, _task, self.organization,
                               performance=self.another_performance)
        test_data = [
            get_data_with_seat(u'A', 1, 0, update_data={u'order.order_no': u'YY0000000000',
                                                        u'performance.code': u'XXIMPRT0101X',
                                                        u'payment_method.name': self.existing_orders[
                                                            0].payment_delivery_pair.payment_method.name,
                                                        u'delivery_method.name': u'RESERVE_NUMBER'})
        ]
        proto_orders, errors = target(test_data)

        self.assertIn('YY0000000000', errors)
        self.assertEquals(errors['YY0000000000'].message, u'更新対象の注文の引取方法と新しい注文の引取方法が異なっています。')

    @mock.patch('altair.app.ticketing.core.api.get_next_order_no')
    def test_transfer(self, get_next_order_no):
        _task = self.get_order_import_task(ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v)
        target = self._makeOne(self.request, self.session, _task, self.organization,
                               performance=self.another_performance)
        update_data = {u'performance.code': u'XXIMPRT0101X'}
        update_data.update(DEFAULT_SHIPPING_ADDRESS)
        test_data_1 = get_data_existing_order(self.existing_orders[0], update_data=update_data)
        product = {
            u'ordered_product.product.name': u'A-B',
            u'ordered_product.price': u'50',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-B-0',
            u'ordered_product_item.price': u'50',
            u'ordered_product_item.quantity': u'1',
            u'seat.name': u'Seat A-5'
        }
        test_data_1[1].update(product)
        test_data_2 = get_data_existing_order(self.existing_orders[1], with_attr=False,
                                              update_data={u'performance.code': u'XXIMPRT0101X'})

        proto_orders, errors = target(test_data_1 + [test_data_2[0]])

        self.assertEqual(errors, {})
        self.assertEqual(len(proto_orders), 2)
        stock_a_quantity = self.stocks[0].stock_status.quantity
        stock_b_quantity = self.stocks[1].stock_status.quantity

        _proto_orders = list(proto_orders.values())
        proto_order = _proto_orders[0]
        self.assertTrue(get_next_order_no.called_with(self.request, self.organization))
        self.assertEqual(proto_order.order_no, 'YY0000000000')
        self.assertEqual(len(proto_order.items), 2)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.items[1].product, self.another_products[1])
        self.assertEqual(proto_order.items[1].elements[0].product_item, self.another_products[1].items[0])
        self.assertEqual(len(proto_order.items[1].elements), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[1].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method,
                         self.payment_delivery_method_pairs[0].payment_method)
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method,
                         self.payment_delivery_method_pairs[0].delivery_method)
        self.assertEqual(proto_order.shipping_address.last_name, u'配送先姓')
        self.assertEqual(proto_order.shipping_address.first_name, u'配送先名')
        self.assertEqual(proto_order.shipping_address.last_name_kana, u'配送先姓(カナ)')
        self.assertEqual(proto_order.shipping_address.first_name_kana, u'配送先名(カナ)')
        self.assertEqual(proto_order.shipping_address.zip, u'郵便番号')
        self.assertEqual(proto_order.shipping_address.country, u'国')
        self.assertEqual(proto_order.shipping_address.prefecture, u'都道府県')
        self.assertEqual(proto_order.shipping_address.city, u'市区町村')
        self.assertEqual(proto_order.shipping_address.address_1, u'住所1')
        self.assertEqual(proto_order.shipping_address.address_2, u'住所2')
        self.assertEqual(proto_order.shipping_address.tel_1, u'電話番号1')
        self.assertEqual(proto_order.shipping_address.tel_2, u'電話番号2')
        self.assertEqual(proto_order.shipping_address.fax, u'FAX')
        self.assertEqual(proto_order.shipping_address.email_1, u'メールアドレス1')
        self.assertEqual(proto_order.shipping_address.email_2, u'メールアドレス2')
        self.assertEqual(proto_order.attributes['key1'], 'value1')
        self.assertEqual(proto_order.attributes['key2'], 'value2')
        self.assertEqual(self.stocks[0].stock_status.quantity, stock_a_quantity)
        self.assertEqual(self.stocks[1].stock_status.quantity, stock_b_quantity)

        proto_order = _proto_orders[1]
        self.assertEqual(proto_order.order_no, 'YY0000000001')
        self.assertEqual(len(proto_order.items), 1)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(len(proto_order.items[0].elements), 1)
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self.assertEqual(len(proto_order.items[0].elements[0].seats), 1)
        self.assertEqual(len(proto_order.items[0].elements[0].tokens), 1)
        self.assertEqual(proto_order.note, u'メモ')
        self.assertEqual(proto_order.payment_delivery_pair.payment_method,
                         self.payment_delivery_method_pairs[0].payment_method)
        self.assertEqual(proto_order.payment_delivery_pair.delivery_method,
                         self.payment_delivery_method_pairs[0].delivery_method)
        self.assertEqual(proto_order.shipping_address.last_name, u'楽天')
        self.assertEqual(proto_order.shipping_address.first_name, u'太郎0')
        self.assertEqual(proto_order.shipping_address.last_name_kana, u'ラクテン')
        self.assertEqual(proto_order.shipping_address.first_name_kana, u'タロウ')
        self.assertEqual(proto_order.shipping_address.zip, u'2510036')
        self.assertEqual(proto_order.shipping_address.country, u'日本')
        self.assertEqual(proto_order.shipping_address.prefecture, u'東京都')
        self.assertEqual(proto_order.shipping_address.city, u'品川区')
        self.assertEqual(proto_order.shipping_address.address_1, u'東五反田5-21-15')
        self.assertEqual(proto_order.shipping_address.address_2, u'メタリオンOSビル')
        self.assertEqual(proto_order.shipping_address.tel_1, u'03-9999-9999')
        self.assertEqual(proto_order.shipping_address.tel_2, u'090-0000-0000')
        self.assertEqual(proto_order.shipping_address.fax, u'03-9876-5432')
        self.assertEqual(proto_order.shipping_address.email_1, u'dev+test000@ticketstar.jp')
        self.assertEqual(proto_order.shipping_address.email_2, u'dev+mobile-test000@ticketstar.jp')
        self.assertEqual(proto_order.membership, self.existing_orders[1].membership)
        self.assertEqual(proto_order.membergroup, self.membergroup)
        self.assertEqual(proto_order.attributes, {})
        self.assertEqual(proto_order.user, self.existing_orders[1].user)

class OrderImporterTest(ImportBaseTestMixin, unittest.TestCase):
    def _getTarget(self):
        from .importer import OrderImporter
        return OrderImporter

    def setUp(self):
        super(OrderImporterTest, self).setUp()
        self.config = testing.setUp(settings={
            'altair.cart.completion_page.temporary_store.cookie_name': 'xxx',
            'altair.cart.completion_page.temporary_store.secret': 'xxx',
            })
        self.config.include('altair.app.ticketing.cart.setup_components')
        self._lookup_plugin = mock.MagicMock()
        self._lookup_plugin_patch1 = mock.patch('altair.app.ticketing.orders.importer.lookup_plugin', new_callable=lambda: self._lookup_plugin)
        self._lookup_plugin_patch2 = mock.patch('altair.app.ticketing.orders.api.lookup_plugin', new_callable=lambda: self._lookup_plugin)
        self._lookup_plugin_patch1.start()
        self._lookup_plugin_patch2.start()

    def tearDown(self):
        self._lookup_plugin_patch1.stop()
        self._lookup_plugin_patch2.stop()
        testing.tearDown()
        _teardown_db()
    
    def test_create_with_seat(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5, update_data={u'order.order_no': u'XX0000000000'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)

    def test_create_quantity_only(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.NoAllocation.v, False, session=self.session)
        test_data = [
            get_data_without_seat(name=u'C-A', quantity=1, update_data={u'order.order_no': u'XX0000000000'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)

    def test_create_fail(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'YY0000000000'}),
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=2,
                               update_data={u'order.order_no': u'XX0000000000'}),
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=4, seat_prefix=u'B',
                               update_data={u'order.order_no': u'XX0000000001'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertIn('YY0000000000', errors)
        self.assertEquals(len(errors['YY0000000000']), 1)
        self.assertEquals(errors['YY0000000000'][0].message, u'すでに同じ予約番号の予約またはカートが存在します。')
        self.assertIn('XX0000000000', errors)
        self.assertEquals(len(errors['XX0000000000']), 1)
        self.assertEquals(errors['XX0000000000'][0].message, u'座席「Seat A-2」(id=3, l0_id=seat-A-2) は予約 YY0000000001 に配席済みです')
        self.assertIn('XX0000000001', errors)
        self.assertEquals(len(errors['XX0000000001']), 1)
        self.assertEquals(errors['XX0000000001'][0].message, u'座席「Seat B-4」の席種「B」は商品明細に紐づいている席種「A」であるべきです')

    def test_update(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Update.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        order = get_data_existing_order(self.existing_orders[0], update_data=DEFAULT_SHIPPING_ADDRESS)
        test_data = order[0]
        test_data.update(
            {
                u'order.total_amount': u'150',
                u'ordered_product.product.name': u'A-B',
                u'ordered_product.price': u'50',
                u'ordered_product.quantity': u'1',
                u'ordered_product_item.product_item.name': u'A-B-0',
                u'ordered_product_item.price': u'50',
                u'ordered_product_item.quantity': u'1',
                u'seat.name': u'Seat A-5'
            }
        )
        task, errors = importer([test_data], self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)

    def test_update_keep_one(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Update.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        order = get_data_existing_order(self.existing_orders[0], update_data=DEFAULT_SHIPPING_ADDRESS)
        test_data = order[0]
        test_data.update(
            {
                u'order.total_amount': u'400',
                u'ordered_product.quantity': u'3',
                u'ordered_product_item.quantity': u'3',
                u'seat.name': u'Seat A-5'
            }
        )
        task, errors = importer([test_data], self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 1)
        self.assertEquals(errors[u'YY0000000000'][0].message, u'自動配席が有効になっていて、かつ一部の座席が指定されています。指定のない座席は自動的に決定されます。 (座席数=1 商品明細数=3)')
        proto_order = task.proto_orders[0]
        self.assertEquals(proto_order.items[0].elements[0].quantity, 3)
        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task) 
        order = self.session.query(Order).filter(Order.order_no == proto_order.order_no).one()
        seats = set(seat.name for seat in order.items[0].elements[0].seats)
        self.assertEquals(len(seats), 3)
        self.assertIn(u'Seat A-5', seats)

    def test_transfer(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({u'performance.code': u'XXIMPRT0101X'})
        order = get_data_existing_order(self.existing_orders[0], update_data=update_data)
        task, errors = importer(order, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)

    def test_transfer_with_same_seats_1(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({u'performance.code': u'XXIMPRT0101X'})
        order = get_data_existing_order(self.existing_orders[0], update_data=update_data)

        task, errors = importer(order, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)
        proto_order = task.proto_orders[0]
        self.assertEqual(proto_order.performance, self.another_performance)
        self.assertEquals(proto_order.items[0].elements[0].quantity, 2)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)
        order = self.session.query(Order).filter(Order.order_no == proto_order.order_no).one()
        seats = set(seat.name for seat in order.items[0].elements[0].seats)
        self.assertEquals(len(seats), 2)
        self.assertIn(u'Seat A-0', seats)
        self.assertIn(u'Seat A-1', seats)

    def test_transfer_with_same_seats_2(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({u'performance.code': u'XXIMPRT0101X'})
        order_1 = get_data_existing_order(self.existing_orders[0], update_data=update_data)
        order_2 = get_data_existing_order(self.existing_orders[1], update_data=update_data)

        task, errors = importer(order_1 + order_2, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 2)
        self.assertEquals(len(errors), 0)

        # order 1: YY00000000
        self.assertEqual(task.proto_orders[0].order_no, u'YY0000000000')
        self.assertEqual(task.proto_orders[0].performance, self.another_performance)
        self.assertEquals(task.proto_orders[0].items[0].elements[0].quantity, 2)
        self.assertEqual(task.proto_orders[0].items[0].product, self.another_products[0])
        self.assertEqual(task.proto_orders[0].items[0].elements[0].product_item, self.another_products[0].items[0])

        # order 2: YY00000001
        self.assertEqual(task.proto_orders[1].order_no, u'YY0000000001')
        self.assertEqual(task.proto_orders[1].performance, self.another_performance)
        self.assertEquals(task.proto_orders[1].items[0].elements[0].quantity, 2)
        self.assertEquals(task.proto_orders[1].items[1].elements[0].quantity, 1)
        self.assertEqual(task.proto_orders[1].items[0].product, self.another_products[0])
        self.assertEqual(task.proto_orders[1].items[1].product, self.another_products[1])
        self.assertEqual(task.proto_orders[1].items[0].elements[0].product_item, self.another_products[0].items[0])
        self.assertEqual(task.proto_orders[1].items[1].elements[0].product_item, self.another_products[1].items[0])

        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)

        # order 1: YY00000000
        order_1 = self.session.query(Order).filter(Order.order_no == task.proto_orders[0].order_no).one()
        seats_1 = set(seat.name for seat in order_1.items[0].elements[0].seats)
        self.assertEquals(len(seats_1), 2)

        # order 2: YY00000001
        order_2 = self.session.query(Order).filter(Order.order_no == task.proto_orders[1].order_no).one()
        seats_2_1 = set(seat.name for seat in order_2.items[0].elements[0].seats)
        self.assertEquals(len(seats_2_1), 2)
        seats_2_2 = set(seat.name for seat in order_2.items[1].elements[0].seats)
        self.assertEquals(len(seats_2_2), 1)

    def test_transfer_quantity_only_to_seats_1(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({
            u'performance.code': u'XXIMPRT0101X',
            u'ordered_product.product.name': u'A-A',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-A-0',
            u'ordered_product_item.quantity': u'1',
        })
        order = get_data_existing_order(self.existing_orders[2], update_data=update_data)
        task, errors = importer(order, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 1)
        print errors
        self.assertEquals(errors[u'YY0000000002'][0].message, u'座席は自動的に決定されます (予定配席数=2)')
        proto_order = task.proto_orders[0]
        self.assertEqual(proto_order.performance, self.another_performance)
        self.assertEquals(proto_order.items[0].elements[0].quantity, 2)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)
        order = self.session.query(Order).filter(Order.order_no == proto_order.order_no).one()
        seats = set(seat.name for seat in order.items[0].elements[0].seats)
        self.assertEquals(len(seats), 2)
        self.assertIn(u'Seat A-0', seats)
        self.assertIn(u'Seat A-1', seats)

    def test_transfer_quantity_only_to_seats_2(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({
            u'performance.code': u'XXIMPRT0101X',
            u'ordered_product.product.name': u'A-A',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-A-0',
            u'ordered_product_item.quantity': u'1',
        })
        order = get_data_existing_order(self.existing_orders[2], update_data=update_data)
        order[0].update({u'seat.name': u'Seat A-6'})
        order[1].update({u'seat.name': u''})
        task, errors = importer(order, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 1)
        self.assertEquals(errors[u'YY0000000002'][0].message, u'自動配席が有効になっていて、かつ一部の座席が指定されています。指定のない座席は自動的に決定されます。 (座席数=1 商品明細数=2)')
        proto_order = task.proto_orders[0]
        self.assertEqual(proto_order.performance, self.another_performance)
        self.assertEquals(proto_order.items[0].elements[0].quantity, 2)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)
        order = self.session.query(Order).filter(Order.order_no == proto_order.order_no).one()
        seats = set(seat.name for seat in order.items[0].elements[0].seats)
        self.assertEquals(len(seats), 2)
        self.assertIn(u'Seat A-0', seats)
        self.assertIn(u'Seat A-6', seats)

    def test_transfer_quantity_only_to_seats_3(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.SameAllocation, False, session=self.session)
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({
            u'performance.code': u'XXIMPRT0101X',
            u'ordered_product.product.name': u'A-A',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-A-0',
            u'ordered_product_item.quantity': u'1',
        })
        order = get_data_existing_order(self.existing_orders[2], update_data=update_data)
        order[0].update({u'seat.name': u'Seat A-6'})
        order[1].update({u'seat.name': u'Seat A-9'})
        task, errors = importer(order, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(len(errors), 0)
        proto_order = task.proto_orders[0]
        self.assertEqual(proto_order.performance, self.another_performance)
        self.assertEquals(proto_order.items[0].elements[0].quantity, 2)
        self.assertEqual(proto_order.items[0].product, self.another_products[0])
        self.assertEqual(proto_order.items[0].elements[0].product_item, self.another_products[0].items[0])
        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)
        order = self.session.query(Order).filter(Order.order_no == proto_order.order_no).one()
        seats = set(seat.name for seat in order.items[0].elements[0].seats)
        self.assertEquals(len(seats), 2)
        self.assertIn(u'Seat A-6', seats)
        self.assertIn(u'Seat A-9', seats)

    def test_transfer_quantity_only_to_seats_4(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Transfer.v, AllocationModeEnum.ReAllocation, False, session=self.session)
        # order 1: YY00000002
        update_data = DEFAULT_SHIPPING_ADDRESS.copy()
        update_data.update({
            u'performance.code': u'XXIMPRT0101X',
            u'ordered_product.product.name': u'A-A',
            u'ordered_product.quantity': u'2',
            u'ordered_product_item.product_item.name': u'A-A-0',
            u'ordered_product_item.quantity': u'1',
        })
        order_1 = get_data_existing_order(self.existing_orders[2], update_data=update_data)

        # order 1: YY00000002
        order_2 = get_data_existing_order(self.existing_orders[3], update_data=update_data)
        order_2[2].update(
            {
                u'ordered_product.product.name': u'A-B',
                u'ordered_product_item.product_item.name': u'A-B-0',
                u'ordered_product.quantity': u'1',
            }
        )

        task, errors = importer(order_1 + order_2, self.operator, self.organization, self.another_performance)
        self.assertEquals(len(task.proto_orders), 2)
        self.assertEquals(len(errors), 2)
        self.assertEquals(errors[u'YY0000000002'][0].message,
                          u'座席は自動的に決定されます (予定配席数=2)')
        self.assertEquals(errors[u'YY0000000003'][0].message,
                          u'座席は自動的に決定されます (予定配席数=2)')
        self.assertEquals(errors[u'YY0000000003'][1].message,
                          u'座席は自動的に決定されます (予定配席数=1)')

        # order 1: YY00000002
        self.assertEqual(task.proto_orders[0].order_no, u'YY0000000002')
        self.assertEqual(task.proto_orders[0].performance, self.another_performance)
        self.assertEquals(task.proto_orders[0].items[0].elements[0].quantity, 2)
        self.assertEqual(task.proto_orders[0].items[0].product, self.another_products[0])
        self.assertEqual(task.proto_orders[0].items[0].elements[0].product_item, self.another_products[0].items[0])

        # order 2: YY00000003
        self.assertEqual(task.proto_orders[1].order_no, u'YY0000000003')
        self.assertEqual(task.proto_orders[1].performance, self.another_performance)
        self.assertEquals(task.proto_orders[1].items[0].elements[0].quantity, 2)
        self.assertEquals(task.proto_orders[1].items[1].elements[0].quantity, 1)
        self.assertEqual(task.proto_orders[1].items[0].product, self.another_products[0])
        self.assertEqual(task.proto_orders[1].items[1].product, self.another_products[1])
        self.assertEqual(task.proto_orders[1].items[0].elements[0].product_item, self.another_products[0].items[0])
        self.assertEqual(task.proto_orders[1].items[1].elements[0].product_item, self.another_products[1].items[0])


        self._lookup_plugin.return_value = (mock.Mock(), mock.Mock(), mock.Mock())
        run_import_task(self.request, task)

        # order 1: YY00000002
        order_1 = self.session.query(Order).filter(Order.order_no == task.proto_orders[0].order_no).one()
        seats_1 = set(seat.name for seat in order_1.items[0].elements[0].seats)
        self.assertEquals(len(seats_1), 2)

        # order 2: YY00000003
        order_2 = self.session.query(Order).filter(Order.order_no == task.proto_orders[1].order_no).one()
        seats_2_1 = set(seat.name for seat in order_2.items[0].elements[0].seats)
        self.assertEquals(len(seats_2_1), 2)

        seats_2_2 = set(seat.name for seat in order_2.items[1].elements[0].seats)
        self.assertEquals(len(seats_2_2), 1)

    def test_cart_setting_ok(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000',
                                            u'order.cart_setting_id': u'default'}),
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=6,
                               update_data={u'order.order_no': u'XX0000000001',
                                            u'order.cart_setting_id': u'event'}),
        ]

        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 2)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_defaults_to_organization_setting_1(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(task.proto_orders[0].cart_setting_id, self.organization.setting.cart_setting_id)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_defaults_to_organization_setting_2(self):
        self.event.setting = EventSetting()
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False,
                                 session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(task.proto_orders[0].cart_setting_id, self.organization.setting.cart_setting_id)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_defaults_to_event_setting(self):
        self.event.setting = EventSetting(cart_setting=self.cart_settings[1])
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 1)
        self.assertEquals(task.proto_orders[0].cart_setting_id, self.event.setting.cart_setting_id)
        self.assertEquals(len(errors), 0)

    def test_cart_setting_nonexistent_fail(self):
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000',
                                            u'order.cart_setting_id': u'NONEXISTENT'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 0)
        self.assertEquals(len(errors), 1)

    def test_cart_setting_duplicate_fail(self):
        from altair.app.ticketing.orders.models import ImportTypeEnum, AllocationModeEnum
        importer = self._makeOne(self.request, ImportTypeEnum.Create.v, AllocationModeEnum.SameAllocation.v, False, session=self.session)
        test_data = [
            get_data_with_seat(name=u'A-A', quantity=1, ticket_idx=5,
                               update_data={u'order.order_no': u'XX0000000000',
                                            u'order.cart_setting_id': u'duplicate'})
        ]
        task, errors = importer(test_data, self.operator, self.organization, self.performance)
        self.assertEquals(len(task.proto_orders), 0)
        self.assertEquals(len(errors), 1)

