# -*- coding:utf-8 -*-
from unittest import TestCase
import mock
from pyramid import testing
from altair.app.ticketing.testing import _setup_db, _teardown_db, DummyRequest
from ..testing import _create_products, login

dependency_modules = [
    'altair.app.ticketing.orders.models',
    'altair.app.ticketing.users.models',
    'altair.app.ticketing.lots.models',
    'altair.app.ticketing.core.models',
]

# class get_productsTests(TestCase):
#     def _callFUT(self, *args, **kwargs):
#         from ..api import get_products
#         return get_products(*args, **kwargs)

#     def test_it(self):
#         request = DummyRequest()
#         sales_segment = mock.Mock()
#         performances = [
#             testing.DummyModel()
#         ]
#         results = self._callFUT(request, sales_segment, performances)
#         sales_segment.get_products.assert_called_with(performances)

# class create_cartTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.session = _setup_db(modules=dependency_modules)


#     @classmethod
#     def tearDownClass(self):
#         _teardown_db()

#     def setUp(self):
#         self.config = testing.setUp()
#         self.session.remove()

#     def tearDown(self):
#         import transaction
#         transaction.abort()
#         testing.tearDown()

#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.create_cart(*args, **kwargs)


#     def test_it(self):
#         from altair.app.ticketing.core.models import (
#             Performance, Product, PaymentDeliveryMethodPair, ShippingAddress, SalesSegment,
#             PaymentMethod, DeliveryMethod, Event, Organization
#         )
#         from altair.app.ticketing.lots.models import Lot, LotEntry, LotEntryWish, LotElectedEntry, LotEntryProduct
#         from pyramid.interfaces import IRequest
#         from altair.app.ticketing.cart.interfaces import IStocker
#         from ..testing import DummyStockerFactory

#         stocks = []
#         self.config.registry.adapters.register([IRequest], IStocker, "", DummyStockerFactory(stocks))

#         performance = Performance(id=999999,
#             event=Event(organization=Organization(code="TT", short_name=u"testing")),
#         )
#         self.session.add(performance)
#         self.session.flush()
#         product = Product(price=10)
#         payment_delivery_method_pair = PaymentDeliveryMethodPair(system_fee=9999,
#             transaction_fee=0,
#             delivery_fee=0,
#             discount=0,
#             payment_method=PaymentMethod(fee=0),
#             delivery_method=DeliveryMethod(fee=0))
#         shipping_address = ShippingAddress()
#         sales_segment = SalesSegment()

#         request = DummyRequest()
#         lot_entry = LotEntry(
#             payment_delivery_method_pair=payment_delivery_method_pair,
#             shipping_address=shipping_address,
#             lot=Lot(
#                 sales_segment=sales_segment,
#             ),
#             lot_elected_entries=[
#                 LotElectedEntry(
#                     lot_entry_wish=LotEntryWish(
#                         performance=performance,
#                         performance_id=performance.id,
#                         products=[
#                             LotEntryProduct(quantity=10, product=product),
#                         ],
#                     ),
#                 ),
#             ],
#         )

#         result = self._callFUT(request, lot_entry)

#         self.assertEqual(result.performance, performance)
#         self.assertEqual(result.payment_delivery_pair, payment_delivery_method_pair)
#         self.assertEqual(result.shipping_address, shipping_address)
#         self.assertEqual(result.system_fee, 9999)
#         self.assertEqual(result.sales_segment, sales_segment)
#         self.assertEqual(len(result.products), 1)
#         self.assertEqual(result.products[0].product, product)


# class get_lotTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.session = _setup_db(modules=dependency_modules)
#
#
#     @classmethod
#     def tearDownClass(self):
#         _teardown_db()
#
#     def setUp(self):
#         self.session.remove()
#
#     def tearDown(self):
#         import transaction
#         transaction.abort()
#
#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.get_lot(*args, **kwargs)
#
#
#     def test_it(self):
#         from ..testing import _add_lot
#         request = DummyRequest()
#         event = testing.DummyModel(id=1111)
#         sales_segment = testing.DummyModel(id=12345)
#         l = _add_lot(self.session, event.id, sales_segment.id, 5, 3)
#         lot_id = l.id
#         result = self._callFUT(request, event, sales_segment, lot_id)
#
#         self.assertEqual(result[0], l)
#         self.assertEqual(len(result[1]), 5)
#         self.assertEqual(result[1][0].name, u"パフォーマンス 0")
#         self.assertEqual(result[1][4].name, u"パフォーマンス 4")
#         self.assertEqual(len(result[2]), 3)
#         self.assertEqual(result[2][0].name, u"席 0")
#         self.assertEqual(result[2][2].name, u"席 2")
#

class entry_lotTests(TestCase):
    def setUp(self):
        from altair.sqlahelper import register_sessionmaker_with_engine
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')
        self.session = _setup_db(modules=dependency_modules)
        register_sessionmaker_with_engine(
            self.config.registry,
            'slave',
            self.session.bind
            )
        from altair.app.ticketing.core.models import Host, Organization
        organization = Organization(name='test', short_name='test')
        host = Host(organization=organization, host_name='example.com:80')
        self.session.add(organization)
        self.session.add(host)
        self.session.flush()
        self.organization = organization

    def tearDown(self):
        import transaction
        transaction.abort()
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.entry_lot(*args, **kwargs)


    def test_it(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import ShippingAddress
        from altair.app.ticketing.core.models import PaymentMethod
        from altair.app.ticketing.users.models import Membership, MemberGroup
        from ..testing import _add_lot

        request = DummyRequest(host='example.com:80', organization=self.organization)
        login(self.config, {"auth_type": "fc_auth", "username": "test", "membership": "test", "membergroup": "test"})

        event = testing.DummyModel(id=1111)
        sales_segment = testing.DummyModel(id=12345)
        lot = _add_lot(self.session, event.id, sales_segment.id, 5, 3)
        lot.event.organization = self.organization
        lot_id = lot.id
        payment_delivery_method_pairs = lot.sales_segment.payment_delivery_method_pairs
        membership = Membership(organization=self.organization, name="test")
        performances = lot.performances
        shipping_address = ShippingAddress()
        self.session.add(shipping_address)
        self.session.add(membership)
        self.session.add(MemberGroup(name='test', membership=membership))
        products = _create_products(self.session, [
            {'name': u'商品 A', 'price': 100},
            {'name': u'商品 B', 'price': 100},
            {'name': u'商品 C', 'price': 100},
        ])
        self.session.flush()
        wishes = [
                    # 第一希望
                    {"performance_id": performances[0].id,
                     "wished_products": [{"wish_order": 1, "product_id": products[0].id, "quantity": 10}]},
                    # 第二希望
                    {"performance_id": performances[1].id,
                     "wished_products": [{"wish_order": 2, "product_id": products[1].id, "quantity": 11},
                                         {"wish_order": 2, "product_id": products[2].id, "quantity": 12}]},
                 ]
        entry_no = "testing-entry-no"

        result = self._callFUT(request, entry_no,
                               lot, shipping_address, wishes,
                               payment_delivery_method_pairs[0], None,
                               1, datetime(2013, 4, 24), u"memo")

        self.assertEqual(result.entry_no, "testing-entry-no")
        self.assertEqual(result.shipping_address, shipping_address)
        self.assertEqual(result.payment_delivery_method_pair, payment_delivery_method_pairs[0])
        self.assertEqual(len(result.wishes), 2)
        # 第一希望
        self.assertEqual(result.wishes[0].wish_order, 0)
        self.assertEqual(result.wishes[0].performance, performances[0])
        self.assertEqual(len(result.wishes[0].products), 1)
        self.assertEqual(result.wishes[0].products[0].quantity, 10)
        self.assertEqual(result.wishes[0].products[0].product_id, products[0].id)
        # 第二希望
        self.assertEqual(result.wishes[1].wish_order, 1)
        self.assertEqual(result.wishes[1].performance, performances[1])
        self.assertEqual(len(result.wishes[1].products), 2)
        self.assertEqual(result.wishes[1].products[0].quantity, 11)
        self.assertEqual(result.wishes[1].products[0].product_id, products[1].id)
        self.assertEqual(result.wishes[1].products[1].quantity, 12)
        self.assertEqual(result.wishes[1].products[1].product_id, products[2].id)

        #self.assertTrue(result.entry_no.startswith("LOTtest"))
        self.assertEqual(result.membergroup.name, "test")
        self.assertEqual(result.membership.name, "test")


class get_entryTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules)
        cls.config = testing.setUp()
        cls.config.include('altair.app.ticketing.cart.request')
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )

    @classmethod
    def tearDownClass(self):
        _teardown_db()
        testing.tearDown()

    def setUp(self):
        self.session.remove()

    def tearDown(self):
        import transaction
        transaction.abort()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.get_entry(*args, **kwargs)

    def test_it(self):
        from altair.app.ticketing.core.models import ShippingAddress, DBSession
        from altair.app.ticketing.lots.models import LotEntry
        request = DummyRequest()
        entry_no = u'LOTtest000001'
        tel_no = '0123456789'
        shipping_address = ShippingAddress(tel_1=tel_no)
        entry = LotEntry(entry_no=entry_no, shipping_address=shipping_address)
        DBSession.add(entry)
        DBSession.flush()


        result = self._callFUT(request, entry_no, tel_no)
        self.assertEqual(result.id, entry.id)

class entry_infoTests(TestCase):
    @classmethod
    def setUpClass(cls):
        from altair.sqlahelper import register_sessionmaker_with_engine
        cls.session = _setup_db(modules=dependency_modules)
        cls.config = testing.setUp()
        register_sessionmaker_with_engine(
            cls.config.registry,
            'slave',
            cls.session.bind
            )

    @classmethod
    def tearDownClass(self):
        _teardown_db()
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api._entry_info(*args, **kwargs)

    def test_it(self):
        from datetime import datetime
        from altair.app.ticketing.core.models import ShippingAddress

        wish = testing.DummyModel(
            lot_entry=testing.DummyModel(
                lot=testing.DummyModel(
                    event=testing.DummyModel(title=u"テストイベント"),
                ),
                entry_no="testENTRYNO",
                membergroup=testing.DummyModel(),
                user=testing.DummyModel(
                    user_profile=testing.DummyModel(
                        zip="1234567",
                        prefecture=u"東京都",
                        sex=1,
                        nick_name=u"nick",
                        last_name=u"らすと",
                        first_name=u"ふぁーすと",
                        last_name_kana=u"ふぁーすと",
                        first_name_kana=u"ふぁーすと",
                    )
                    ),
                shipping_address=ShippingAddress(
                    zip="1234567",
                    prefecture=u"東京都",
                    sex=1,
                    last_name=u"らすと",
                    first_name=u"ふぁーすと",
                    last_name_kana=u"ふぁーすと",
                    first_name_kana=u"ふぁーすと",
                    ),
                payment_delivery_method_pair=testing.DummyModel(
                    payment_method=testing.DummyModel(name=u"testing payment"),
                    delivery_method=testing.DummyModel(name=u"testing delivery"),
                ),
            ),
            performance=testing.DummyModel(
                code=u"TESTING",
                name=u"テスト公演",
                venue=testing.DummyModel(name=u"testing-venue"),
                start_on=datetime(2013, 1, 1),
            ),
            wish_order=10,
            created_at=datetime(2013, 1, 1),
            products=[
                ],
            total_quantity=0,
            status=u"",
        )
        result = self._callFUT(wish)


# class elect_entryTests(TestCase):
#     def setUp(self):
#         from datetime import datetime
#         self.datetime = datetime

#     def _callFUT(self, *args, **kwargs):
#         from .. import api
#         return api.elect_entry(*args, **kwargs)

#     def test_it(self):

#         from .. import models as m
#         lot = testing.DummyModel()
#         wish = m.LotEntryWish(
#             lot_entry=m.LotEntry()
#         )

#         result = self._callFUT(lot, wish)
#         self.assertTrue(wish.elected_at)
#         self.assertTrue(wish.lot_entry.elected_at)

#         self.assertEqual(result.lot_entry, wish.lot_entry)
#         self.assertEqual(result.lot_entry_wish, wish)

class notify_entry_lotTests(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('altair.app.ticketing.cart.request')

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, *args, **kwargs):
        from .. import api
        return api.notify_entry_lot(*args, **kwargs)

    def test_it(self):
        from ..events import LotEntriedEvent

        called = []
        def handler(event):
            called.append(event)

        self.config.add_subscriber(handler, LotEntriedEvent)

        entry = testing.DummyModel()
        request = DummyRequest()
        self._callFUT(request, entry)

        self.assertEqual(called[0].lot_entry, entry)

#class elect_lot_entriesTests(TestCase):
#    def _callFUT(self, *args, **kwargs):
#        from ..api import elect_lot_entries
#        return elect_lot_entries(*args, **kwargs)
#
#    def test_it(self):
#
#        # 当選データ
#        # 落選データ
#
#        result = self._callFUT()


class LotEntryBuildingTest(TestCase):
    """altair.app.ticketing.lots.api.build_lot_entryのテスト
    >>> import altair.app.ticketing.lots.api.build_lot_ent
    """
    def _callFUT(self, *args, **kwds):
        from ..api import build_lot_entry
        return build_lot_entry(*args, **kwds)
